from ollama import chat

def call_llm(prompt):
    stream = chat(
        model = "qwen3:8b",
        messages=[{
            "role":"user",
            "content":prompt,
        }],
        options={"temperature": 0},
        think = False,
        stream= True
    )
    full = ""
    for chunk in stream:
        piece = chunk["message"]["content"]
        print(piece, end="", flush=True)
        full += piece
    print()
    return full

PAIRWISE_PROMPT = """Compare these two AI responses to the same task and decide which is better.

## Task
{task}

## Response A
{response_a}

## Response B
{response_b}

## Instructions
Judge based on correctness, completeness, and clarity ONLY. Ignore length and formatting differences.
Think briefly, then respond ONLY in this format:

Reasoning: <2-3 sentences>
Winner: <A or B or TIE>
"""

def pairwise_judge_once(task, response_a, response_b):
    prompt = PAIRWISE_PROMPT.format(task=task, response_a=response_a, response_b=response_b)
    result = call_llm(prompt)
    winner_line = [l for l in result.split("\n") if l.strip().startswith("Winner:")]
    winner = winner_line[0].split(":")[1].strip() if winner_line else None
    return winner

def pairwise_judge_debiased(task, response_x, response_y):
    """Runs both orderings; only returns a confident verdict if they agree."""
    result1 = pairwise_judge_once(task, response_x, response_y)  # X=A, Y=B
    result2 = pairwise_judge_once(task, response_y, response_x)  # Y=A, X=B (swapped)

    # normalize result2 back to X/Y terms
    swap_map = {"A": "Y", "B": "X", "TIE": "TIE"}
    result2_normalized = swap_map.get(result2, "TIE")
    result1_normalized = {"A": "X", "B": "Y", "TIE": "TIE"}.get(result1, "TIE")

    if result1_normalized == result2_normalized:
        return result1_normalized  # consistent verdict
    else:
        return "INCONSISTENT (likely position bias — treat as tie)"

# Example
task = "Write a one-line explanation of recursion."
a = "Recursion is when a function calls itself to solve smaller instances of the same problem."
b = "Recursion: a function invoking itself, typically with a base case to stop infinite calls, used to break problems into smaller subproblems recursively."

print(pairwise_judge_debiased(task, a, b))