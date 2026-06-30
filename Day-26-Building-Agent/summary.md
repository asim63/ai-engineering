# Day 29 — Building Your First Agent: Multiple Tools, Real Decision Making

## What I Built Today
A fully working research agent with 4 tools (web_search, read_file, write_file, calculate)
and a done tool, with max iteration limits, error handling, logging, and real multi-step
task execution. Tested from simple math to multi-source research tasks to intentional failures.

---

## 1. What Makes Today Different from Yesterday

Yesterday's agent had one tool and did simple math.
Today's agent has 4 tools, a system prompt, logging, max iterations, error handling,
and can autonomously plan and execute multi-step research tasks.

The agent given this task:
```
"Research the differences between GPT and BERT, their applications,
and write a detailed comparison to gpt_vs_bert.md"
```

Planned and executed this on its own:
```
Iteration 1 → web_search("differences between GPT and BERT architectures")
Iteration 2 → web_search("real world applications of GPT and BERT")
Iteration 3 → write_file("gpt_vs_bert.md", "...full comparison...")
Iteration 4 → done("Completed research and wrote comparison")
```

No instructions on which tools to use or in what order. The agent decided.

---

## 2. The Four Tool Functions

Simple Python functions. Nothing special — the agent loop calls these when the model
requests them.

```python
def web_search(query: str) -> str:
    try:
        results = tavily.search(query=query, max_results=3)
        output = ""
        for r in results["results"]:
            output += f"Title: {r['title']}\n"
            output += f"URL: {r['url']}\n"
            output += f"Content: {r['content']}\n"
            output += "-" * 40 + "\n"
        return output
    except Exception as e:
        return f"Search error: {e}"


def read_file(filepath: str) -> str:
    try:
        with open(filepath, encoding="utf-8", mode="r") as file:
            return file.read()
    except FileNotFoundError:
        return f"Error: File '{filepath}' not found."
    except Exception as e:
        return f"Error occurred: {e}"


def write_file(filepath: str, content: str) -> str:
    try:
        with open(filepath, encoding="utf-8", mode="w") as file:
            file.write(content)
            return f"Successfully written to '{filepath}'"
    except Exception as e:
        return f"Error occurred: {e}"


def calculate(expression: str) -> str:
    try:
        result = eval(expression)
        return str(result)
    except Exception as e:
        return f"Error occurred: {e}"
```

**Key point:** every function returns a string — success message, result, or error.
The agent loop sends whatever string comes back to the model as the tool result.
The model reads it and decides what to do next, including reading error messages
and adapting.

---

## 3. The Done Tool

A special tool the model calls when it thinks the task is complete.
It takes a summary of what was accomplished.

```python
# In tool definitions:
{
    "type": "function",
    "function": {
        "name": "done",
        "description": "Call this when the task is fully complete and you have nothing left to do.",
        "parameters": {
            "type": "object",
            "properties": {
                "summary": {
                    "type": "string",
                    "description": "A short summary of what you accomplished."
                }
            },
            "required": ["summary"]
        }
    }
}

# In route_tool:
elif tool_name == "done":
    result = "DONE"
```

When the router returns "DONE", the agent loop checks for it and stops.
This gives the model control over when to stop rather than just running out of iterations.

**Problem hit:** qwen3:8b was writing `<done>` as text instead of calling the tool.
**Fix:** added an else block that nudges the model back when it drifts to text responses.

---

## 4. The Tool Router

One function that receives tool name + arguments from the model
and calls the right Python function:

```python
def route_tool(tool_name: str, tool_args: dict) -> str:
    print(f"  [TOOL] {tool_name} called with {tool_args}")

    if tool_name == "web_search":
        result = web_search(tool_args["query"])
    elif tool_name == "read_file":
        result = read_file(tool_args["filepath"])
    elif tool_name == "write_file":
        result = write_file(tool_args["filepath"], tool_args["content"])
    elif tool_name == "calculate":
        result = calculate(tool_args["expression"])
    elif tool_name == "done":
        result = "DONE"
    else:
        result = f"Error: Unknown tool '{tool_name}'"

    print(f"  [RESULT] {result[:100]}")
    return result
```

The print statements are your logging — every tool call and result is visible
in the terminal so you can follow exactly what the agent is doing.

---

## 5. The Full Agent Loop

```python
def run_agent(task: str, max_iterations: int = 10):
    print(f"\n{'='*50}")
    print(f"TASK: {task}")
    print(f"{'='*50}\n")

    messages = [
        {
            "role": "system",
            "content": """You are a research agent with access to tools.
IMPORTANT RULES:
- Always use tools to complete tasks, never respond with plain text until done.
- You MUST call the 'done' tool when the task is complete.
- Do NOT write <done> or any text. ONLY call the done tool.
- After getting a tool result that completes the task, immediately call done."""
        },
        {
            "role": "user",
            "content": task
        }
    ]

    iteration = 0

    while iteration < max_iterations:
        iteration += 1
        print(f"\n--- Iteration {iteration}/{max_iterations} ---")

        response = chat(
            model="qwen3:8b",
            messages=messages,
            tools=tools
        )

        message = response["message"]
        messages.append(message)

        if message.get("tool_calls"):
            for tool_call in message["tool_calls"]:
                tool_name = tool_call["function"]["name"]
                tool_args = tool_call["function"]["arguments"]

                result = route_tool(tool_name, tool_args)

                if tool_name == "done":
                    print(f"\n{'='*50}")
                    print(f"AGENT DONE after {iteration} iterations")
                    print(f"Summary: {tool_args.get('summary')}")
                    print(f"{'='*50}")
                    return

                messages.append({
                    "role": "tool",
                    "content": result
                })

        else:
            # Model gave text instead of calling done — nudge it back
            print(f"\n[MODEL] {message['content'][:100]}")
            messages.append({
                "role": "user",
                "content": "You must call the 'done' tool now to complete the task. Do not respond with text."
            })

    print(f"\nMax iterations ({max_iterations}) reached. Stopping.")
```

---

## 6. Max Iterations — Why It Matters

Without a limit, a confused agent can loop forever — calling tools repeatedly,
going in circles, burning API credits or compute.

```python
while iteration < max_iterations:   # hard stop at 10
```

In production systems this is non-negotiable. You always set a ceiling.
10 is reasonable for most tasks. Complex research tasks might need 15-20.

---

## 7. Error Handling

Every tool function returns an error string instead of crashing:

```python
except FileNotFoundError:
    return f"Error: File '{filepath}' not found."
```

That error string goes back to the model as the tool result. The model reads it,
understands what went wrong, and decides what to do — try a different path,
give up gracefully, or ask for clarification.

**Tested with intentional failure:**
```
Task: Read secret_data.txt, calculate sum of numbers, save to output.txt

Iteration 1 → read_file("secret_data.txt") → Error: File not found
Iteration 2 → read_file("Day-26-Building-Agent\secret_data.txt") → Error: File not found
Iteration 3 → done("File could not be found. Please verify the path.")
```

The agent tried a recovery path, accepted failure gracefully, and reported back.
No crash, no infinite loop, no hallucinated result.

---

## 8. Working Directory Issue

When the agent writes a file with just a filename (`transformer_summary.md`),
it resolves relative to wherever the script is run from — not the Day folder.

**Fix — set working directory at the start of run_agent:**
```python
import os
os.chdir(r"D:\Projects\ai-engineering\Day-26-Building-Agent")
```

Now all file reads and writes resolve inside the Day folder regardless of
where you run the script from.

---

## 9. When Agents Are Overkill

| Use agents when | Skip agents when |
|---|---|
| Task requires multiple steps | Single question, single answer |
| Steps unknown in advance | Fixed pipeline always works |
| Needs real world data | Knowledge already in the model |
| Each step depends on previous results | No decision making needed |
| Tool selection varies by task | Same tools always called in same order |

Your RAG pipeline from last week is NOT an agent — it always does the same
steps in the same order. An agent would be overkill there. Knowing when NOT
to use agents is as important as knowing how to build them.

---


