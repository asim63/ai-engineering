import pandas as pd
import json
import re
import traceback
import matplotlib
import matplotlib.pyplot as plt

def load_csv(path: str) -> pd.DataFrame:
    """Load a CSV and auto-upgrade text columns that are actually dates."""
    df = pd.read_csv(path)
    for col in df.columns:
        if pd.api.types.is_object_dtype(df[col]) or pd.api.types.is_string_dtype(df[col]):
            try:
                converted = pd.to_datetime(df[col], errors="raise")
                if converted.notna().mean() > 0.9:
                    df[col] = converted
            except (ValueError, TypeError):
                pass
    return df


def profile_dataframe(df: pd.DataFrame, sample_rows: int = 3) -> dict:
    """Build a structured profile: dtypes, nulls, sample/distinct values, ranges."""
    profile = {"n_rows": len(df), "n_columns": len(df.columns), "columns": {}}
    for col in df.columns:
        series = df[col]
        col_info = {
            "dtype": str(series.dtype),
            "n_nulls": int(series.isna().sum()),
            "n_unique": int(series.nunique()),
        }
        if pd.api.types.is_numeric_dtype(series):
            col_info["min"] = float(series.min()) if series.notna().any() else None
            col_info["max"] = float(series.max()) if series.notna().any() else None
        elif pd.api.types.is_datetime64_any_dtype(series):
            col_info["min_date"] = str(series.min())
            col_info["max_date"] = str(series.max())
        elif series.nunique() <= 20:
            col_info["distinct_values"] = series.dropna().unique().tolist()
        profile["columns"][col] = col_info
    return profile


def profile_to_prompt_text(profile: dict, table_name: str = "df") -> str:
    """Render the profile into compact text for an LLM prompt."""
    lines = [f"Table: {table_name}", f"Rows: {profile['n_rows']}", "Columns:"]
    for col, info in profile["columns"].items():
        parts = [f"  - {col} ({info['dtype']})"]
        if "distinct_values" in info:
            parts.append(f"values={info['distinct_values']}")
        elif "min" in info:
            parts.append(f"range=[{info['min']}, {info['max']}]")
        elif "min_date" in info:
            parts.append(f"range=[{info['min_date']} to {info['max_date']}]")
        if info["n_nulls"] > 0:
            parts.append(f"nulls={info['n_nulls']}")
        lines.append(" ".join(parts))
    return "\n".join(lines)



import ollama  # pip install ollama — official client, talks to the local server for you

OLLAMA_MODEL = "qwen3:8b"


def call_ollama(prompt: str, model: str = OLLAMA_MODEL) -> str:
    """Send a prompt to a locally running Ollama server using the official client.
    This is the 'drop-in OpenAI-style' interface your roadmap points at:
    same shape as openai.chat.completions.create(...) or anthropic.messages.create(...).
    Requires: `ollama serve` running, and `ollama pull qwen3:8b` already done."""
    response = ollama.chat(
        model=model,
        messages=[{"role": "user", "content": prompt}],
        options={"temperature": 0},  # 0 = deterministic, best for code generation
    )
    return response["message"]["content"]


CODE_GEN_PROMPT_TEMPLATE = """You are a data analyst. You are given a pandas DataFrame called `df`.

{schema}

Question: {question}

Write Python pandas code that computes the answer and stores it in a variable called `result`.
Rules:
- Only use the column names shown above, exactly as spelled.
- Do not read any file, `df` already exists.
- Do not print anything, just assign the final answer to `result`.
- Return ONLY the Python code, no explanation, no markdown fences.
"""


def build_code_gen_prompt(question: str, profile: dict, table_name: str = "df") -> str:
    schema = profile_to_prompt_text(profile, table_name=table_name)
    return CODE_GEN_PROMPT_TEMPLATE.format(schema=schema, question=question)


def extract_code(llm_response: str) -> str:
    """LLMs often wrap code in ```python ... ``` even when told not to. Strip that off.
    Also strips qwen3's <think>...</think> reasoning blocks if present."""
    text = re.sub(r"<think>.*?</think>", "", llm_response, flags=re.DOTALL)
    match = re.search(r"```(?:python)?\s*(.*?)```", text, re.DOTALL)
    if match:
        return match.group(1).strip()
    return text.strip()


def execute_code(code: str, df: pd.DataFrame):
    """Run LLM-generated code in a restricted namespace.
    Returns (success: bool, result_or_error)."""
    safe_globals = {
        "pd": pd,
        "__builtins__": {
            # only the builtins needed for typical data-analysis code
            "len": len, "sum": sum, "min": min, "max": max, "round": round,
            "sorted": sorted, "list": list, "dict": dict, "str": str,
            "int": int, "float": float, "range": range, "abs": abs,
        },
    }
    local_vars = {"df": df}
    try:
        exec(code, safe_globals, local_vars)
        if "result" not in local_vars:
            return False, "Code ran but did not set a `result` variable."
        return True, local_vars["result"]
    except Exception:
        return False, traceback.format_exc()


FIX_PROMPT_TEMPLATE = """Your previous code failed when run.

{schema}

Question: {question}

Code that failed:
```
{code}
```

Error it produced:
{error}

Fix the code. Return ONLY the corrected Python code, no explanation, no markdown fences.
Remember: store the final answer in a variable called `result`.
"""


def ask_question(question: str, df: pd.DataFrame, profile: dict,
                  llm_fn=call_ollama, max_retries: int = 3, table_name: str = "df"):
    """Full Step 2-4 loop: generate code, run it, self-heal on failure.
    llm_fn is swappable so we can test with a fake LLM."""
    prompt = build_code_gen_prompt(question, profile, table_name=table_name)
    code = extract_code(llm_fn(prompt))
    attempts = [{"attempt": 1, "code": code}]

    for attempt_num in range(1, max_retries + 1):
        success, outcome = execute_code(code, df)
        attempts[-1]["success"] = success
        attempts[-1]["outcome"] = str(outcome)[:300]

        if success:
            return {"success": True, "result": outcome, "code": code, "attempts": attempts}

        if attempt_num == max_retries:
            break  # out of retries, fall through to failure return

        fix_prompt = FIX_PROMPT_TEMPLATE.format(
            schema=profile_to_prompt_text(profile, table_name=table_name),
            question=question, code=code, error=outcome,
        )
        code = extract_code(llm_fn(fix_prompt))
        attempts.append({"attempt": attempt_num + 1, "code": code})

    return {"success": False, "result": None, "code": code, "attempts": attempts}


EXPLAIN_PROMPT_TEMPLATE = """You are a data analyst reporting a finding to a non-technical colleague.

Question asked: {question}
Code used to answer it:
{code}
Raw result: {result}

Write a short, plain-English explanation (1-3 sentences) of what the answer means.
Do not mention code or pandas. Just state the finding naturally, as if talking to a colleague.
"""


def explain_result(question: str, code: str, result, llm_fn=call_ollama) -> str:
    prompt = EXPLAIN_PROMPT_TEMPLATE.format(question=question, code=code, result=result)
    raw = llm_fn(prompt)
    return re.sub(r"<think>.*?</think>", "", raw, flags=re.DOTALL).strip()


def answer_question(question: str, df: pd.DataFrame, profile: dict,
                     llm_fn=call_ollama, table_name: str = "df") -> dict:
    """The full user-facing flow: Steps 2-5 combined."""
    outcome = ask_question(question, df, profile, llm_fn=llm_fn, table_name=table_name)
    if not outcome["success"]:
        return {**outcome, "explanation": "Sorry, I couldn't compute an answer after several attempts."}
    explanation = explain_result(question, outcome["code"], outcome["result"], llm_fn=llm_fn)
    return {**outcome, "explanation": explanation}


TREND_KEYWORDS = ["trend", "over time", "monthly", "weekly", "daily", "growth",
                   "change over", "plot", "chart", "graph", "visualize"]


def wants_chart(question: str) -> bool:
    """Simple, fast, cheap check first (no LLM call needed for the common case)."""
    q = question.lower()
    return any(kw in q for kw in TREND_KEYWORDS)


CHART_CODE_PROMPT_TEMPLATE = """You are a data analyst. You are given a pandas DataFrame called `df`
and matplotlib.pyplot already imported as `plt`.

{schema}

Question: {question}

Write Python code that creates a matplotlib chart answering this question, and saves it to a file
called 'chart_output.png' using plt.savefig('chart_output.png'). Then close the figure with plt.close().
Rules:
- Only use the column names shown above, exactly as spelled.
- If a date column is involved, group by an appropriate time period (e.g. month) before plotting.
- Do not call plt.show().
- Also assign a short text summary of the chart to a variable called `result`.
- Return ONLY the Python code, no explanation, no markdown fences.
"""


def execute_chart_code(code: str, df: pd.DataFrame):
    """Like execute_code, but also allows matplotlib (plt) in the sandbox."""
    import matplotlib
    matplotlib.use("Agg")
    

    safe_globals = {
        "pd": pd, "plt": plt,
        "__builtins__": {
            "len": len, "sum": sum, "min": min, "max": max, "round": round,
            "sorted": sorted, "list": list, "dict": dict, "str": str,
            "int": int, "float": float, "range": range, "abs": abs,
        },
    }
    local_vars = {"df": df}
    try:
        exec(code, safe_globals, local_vars)
        result_text = local_vars.get("result", "Chart generated.")
        return True, result_text
    except Exception:
        return False, traceback.format_exc()


def answer_question_with_chart(question: str, df: pd.DataFrame, profile: dict,
                                llm_fn=call_ollama, max_retries: int = 3,
                                table_name: str = "df") -> dict:
    """Routes to chart generation if the question looks like a trend question,
    otherwise falls back to the normal answer_question flow."""
    if not wants_chart(question):
        return answer_question(question, df, profile, llm_fn=llm_fn, table_name=table_name)

    prompt = CHART_CODE_PROMPT_TEMPLATE.format(
        schema=profile_to_prompt_text(profile, table_name=table_name), question=question
    )
    code = extract_code(llm_fn(prompt))
    attempts = [{"attempt": 1, "code": code}]

    for attempt_num in range(1, max_retries + 1):
        success, outcome = execute_chart_code(code, df)
        attempts[-1]["success"] = success
        attempts[-1]["outcome"] = str(outcome)[:300]
        if success:
            explanation = explain_result(question, code, outcome, llm_fn=llm_fn)
            return {"success": True, "result": outcome, "chart_path": "chart_output.png",
                    "code": code, "attempts": attempts, "explanation": explanation}
        if attempt_num == max_retries:
            break
        fix_prompt = FIX_PROMPT_TEMPLATE.format(
            schema=profile_to_prompt_text(profile, table_name=table_name),
            question=question, code=code, error=outcome,
        )
        code = extract_code(llm_fn(fix_prompt))
        attempts.append({"attempt": attempt_num + 1, "code": code})

    return {"success": False, "result": None, "code": code, "attempts": attempts,
            "explanation": "Sorry, I couldn't generate the chart after several attempts."}


if __name__ == "__main__":
    df = load_csv(r"Day-35-Project5\sales_data.csv")
    profile = profile_dataframe(df)
    print("=== STEP 1 CHECK ===")
    print(profile_to_prompt_text(profile, table_name="sales"))

    print("\n=== STEP 2 CHECK (prompt only, no live model here) ===")
    question = "Which product had the highest revenue?"
    prompt = build_code_gen_prompt(question, profile, table_name="df")
    print(prompt)

    print("\n=== STEP 3 CHECK: execute a hand-written stand-in for what the LLM would return ===")
    fake_llm_code = """
totals = df.groupby('product')['revenue'].sum().sort_values(ascending=False)
result = totals.index[0]
"""
    ok, result = execute_code(fake_llm_code, df)
    print("success:", ok, "| result:", result)

    print("\n--- now testing what happens when the code is BROKEN (wrong column name) ---")
    broken_code = "result = df.groupby('produkt')['revenue'].sum()"  # typo on purpose
    ok, result = execute_code(broken_code, df)
    print("success:", ok)
    print("error message:\n", result)

    print("\n=== STEP 4 CHECK: retry loop with a fake LLM that fails once, then self-fixes ===")
    call_count = {"n": 0}

    def fake_llm_that_fails_then_fixes(prompt: str) -> str:
        call_count["n"] += 1
        if call_count["n"] == 1:
            # simulate the model guessing a wrong column name on the first try
            return "result = df.groupby('produkt')['revenue'].sum().idxmax()"
        # simulate it correcting itself after seeing the error
        return "result = df.groupby('product')['revenue'].sum().idxmax()"

    outcome = ask_question(
        "Which product had the highest revenue?", df, profile,
        llm_fn=fake_llm_that_fails_then_fixes,
    )
    print("Final success:", outcome["success"])
    print("Final result:", outcome["result"])
    print("Number of attempts:", len(outcome["attempts"]))
    for a in outcome["attempts"]:
        print(f"  attempt {a['attempt']}: success={a.get('success')} outcome={a.get('outcome')}")
        
    print("\n=== STEP 5 LIVE CHECK: full answer + explanation ===")
    outcome = answer_question("Which product had the highest revenue?", df, profile)
    print("Result:", outcome["result"])
    print("Explanation:", outcome["explanation"])

    # print("\n=== STEP 6 LIVE CHECK: chart generation ===")
    # chart_outcome = answer_question_with_chart("Show me the monthly revenue trend", df, profile)
    # print("Success:", chart_outcome["success"])
    # print("Explanation:", chart_outcome.get("explanation"))
    # print("Code:\n", chart_outcome["code"])