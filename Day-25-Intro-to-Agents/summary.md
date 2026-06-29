# Day 28 — Introduction to Agents and Tool Use

## What I Built Today
A working AI Agent from scratch using Ollama + qwen3:8b with a calculator tool.
The agent demonstrates the full ReAct loop — deciding when to use tools,
running them, observing results, and reasoning through multi-step problems
without any hardcoded instructions on when to call what.

---

## 1. What is an Agent?

My intuition going in: "something that works by itself without human intervention" — correct.

A regular LLM call is one shot:
```
You ask → It answers → Done
```

An agent is an LLM inside a loop:
```
You ask → It thinks → It uses a tool → It sees the result → It thinks again → repeat → It answers
```

That loop — **think → act → observe → think again** — is what makes it an agent,
not just a chatbot.

**The three things every agent needs:**

| Part | What it does | Without it |
|------|-------------|------------|
| LLM | The brain — decides what to do | Just a script |
| Tools | How it interacts with the world | Just a chatbot |
| Memory | Conversation history between steps | Loops forever, forgets what it did |

---

## 2. How Agents Differ from RAG

This was an important realization. My RAG system was already close to an agent:
- It has retrieval tools
- An LLM reasons over results
- There's a loop

**The key difference:**

| | RAG System | Agent |
|---|---|---|
| Pipeline | Fixed — always: retrieve → rerank → answer | Flexible — LLM decides |
| Tool use | Always called, in order | Called only when needed, in any order |
| Steps | Predictable | Unpredictable |

RAG = fixed pipeline. Agent = LLM decides the pipeline on the fly.

---

## 3. The ReAct Pattern

**ReAct = Reasoning + Acting**

The most common agent architecture. The LLM follows this pattern:

```
Thought:     I need to calculate 15% of 847 first.
Action:      calculator("0.15 * 847")
Observation: 127.05

Thought:     Now add 231 to that result.
Action:      calculator("127.05 + 231")
Observation: 358.05

Thought:     I have everything I need to answer.
Final Answer: 15% of 847 is 127.05. Adding 231 gives 358.05.
```

**Reason** about what to do → **Act** by calling a tool → **Observe** the result → repeat.
This is the loop. The model keeps going until it decides it has enough to answer.

---

## 4. Defining a Tool

A tool is just a Python dictionary — metadata that tells the LLM:
1. What the tool is called
2. When to use it
3. What inputs it needs

```python
calculator_tool = {
    "type": "function",
    "function": {
        "name": "calculator",
        "description": "Performs arithmetic calculations. Use this for ANY math operation — addition, subtraction, multiplication, division, percentages, powers. Always use this instead of calculating yourself.",
        "parameters": {
            "type": "object",
            "properties": {
                "expression": {
                    "type": "string",
                    "description": "The math expression to evaluate. Examples: '23 * 47', '100 / 4', '2 ** 10'"
                }
            },
            "required": ["expression"]
        }
    }
}
```

**Breaking down each part:**

- `name` — what the model calls the tool by. Like a function name.
- `description` — **the most critical part**. The model reads this to decide whether and when to call the tool. Vague description = model won't know when to use it. Write it as instructions for the LLM, not for a human.
- `parameters.properties` — every input the function needs. Each property has a `type` and `description`.
- `required` — list of which properties must always be provided.

**Common property types:** `string`, `number`, `boolean`

---

## 5. Ollama vs Anthropic Tool Format

Same concept, two small naming differences:

| | Ollama | Anthropic |
|---|---|---|
| Wrapper | `{"type": "function", "function": {...}}` | Just the inner dict directly |
| Schema key | `parameters` | `input_schema` |
| Result role | `"tool"` | `"tool_result"` |
| Needs ID? | No | Yes — must reference `tool_use_id` |

Once you understand the concept with Ollama, switching to Anthropic is just
learning two new key names. The thinking is identical.

---

## 6. The Actual Python Function

The tool definition is just metadata — the LLM never runs your code.
It just says "I want to call calculator with this expression."
You run the actual function and return the result.

```python
def calculator(expression: str) -> str:
    try:
        result = eval(expression)
        return str(result)           # return as string to send back to model
    except Exception as e:
        return f"Error: {e}"
```

`eval()` runs a string as Python code. Returns float when any decimal is involved,
int when all values are whole numbers — that's just Python's type system.

---

## 7. What the Model Response Actually Looks Like

This is what `response["message"]` contains in each case:

**When the model decides to call a tool:**
```python
{
    "role": "assistant",
    "content": "",               # empty — no text answer yet
    "tool_calls": [              # ← this appears
        {
            "function": {
                "name": "calculator",
                "arguments": {
                    "expression": "1234 * 5678"
                }
            }
        }
    ]
}
```

**When the model gives a final answer:**
```python
{
    "role": "assistant",
    "content": "1234 × 5678 = 7,006,652",   # ← normal text
    "tool_calls": None                        # ← absent or None
}
```

So `message.get("tool_calls")` is the check — did the model respond with
a tool request or a final answer?

---

## 8. The Agent Loop — Full Code

```python
def run_agent(user_message: str):
    messages = [{"role": "user", "content": user_message}]

    print(f"\nUser: {user_message}")

    while True:
        response = chat(
            model="qwen3:8b",
            messages=messages,
            tools=[calculator_tool]
        )

        message = response["message"]
        messages.append(message)        # always append to history

        if message.get("tool_calls"):   # model wants to use a tool
            for tool_call in message["tool_calls"]:
                tool_name = tool_call["function"]["name"]
                tool_args = tool_call["function"]["arguments"]

                print(f"\n→ Model calls: {tool_name}")
                print(f"→ With: {tool_args}")

                # Tool router — which function to actually run
                if tool_name == "calculator":
                    result = calculator(tool_args["expression"])
                else:
                    result = "Tool not found"

                print(f"→ Result: {result}")

                # Send result back to model
                messages.append({
                    "role": "tool",
                    "content": result
                })
            # Loop continues — model reads result and thinks again

        else:
            # No tool call = model is done reasoning
            print(f"\nFinal Answer: {message['content']}")
            break
```

**Why `while True`?** You don't know in advance how many tool calls the model
will make. Could be 1, could be 5. The loop runs until the model stops calling
tools and gives a text answer.

**Why append every message?** The model has no memory between API calls.
The entire conversation history — including tool calls and results — must be
sent with every request so the model knows what it already did.

---

## 9. Tool Call IDs

When the model calls multiple tools, each call can get a unique ID so results
can be matched back to the right call.

**Ollama** — IDs may be None. Results matched by order. Simple for learning.

**Anthropic** — each call gets an ID like `toolu_abc123`.
When you send results back you must reference that ID:

```python
# Anthropic style — matching result to call using ID
messages.append({
    "role": "user",
    "content": [{
        "type": "tool_result",
        "tool_use_id": "toolu_abc123",   # must match the original call
        "content": "7006652"
    }]
})
```

Why does this matter? When multiple tools fire simultaneously, the model needs
to know which result belongs to which call. Without IDs it can't tell them apart.

---

## 10. Multi-Tool Calls

The model can call the same tool (or different tools) multiple times in one response.
The `for tool_call in message["tool_calls"]` loop handles this automatically.

**Tested:**
```
User: First tell me what 1234 * 5678 is, then separately what 8765 * 4321 is

→ Model calls: calculator  {'expression': '1234 * 5678'}  → 7006652
→ Model calls: calculator  {'expression': '8765 * 4321'}  → 37873565

Final Answer: 1234 × 5678 = 7,006,652 and 8765 × 4321 = 37,873,565
```

Both calls happened in the **same loop iteration** — the model batched them
before giving the final answer. That's multi-tool calling.

**Also observed:** when asked "what is 15% of 847, then add 231",
the model was smart enough to combine it into one expression `(0.15 * 847) + 231`
instead of two separate calls. The model reasons about efficiency on its own.

---

## The Full Agent Flow

```
User Query
    │
    ▼
LLM reads query + tool definitions
    │
    ├── Decides to call tool
    │       │
    │       ▼
    │   Returns tool_calls block (not text)
    │       │
    │       ▼
    │   Your Python function runs
    │       │
    │       ▼
    │   Result appended as "tool" message
    │       │
    │       ▼
    │   LLM reads result → decides again
    │       │
    │       └── needs more tools? → loop back up
    │
    └── Has enough to answer → returns text → break
```

---
