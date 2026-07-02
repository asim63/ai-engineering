# Day 31 — Multi-Agent Systems: Concepts and Basics

## What I Built Today
A 2-agent pipeline system (researcher + writer) with shared state and human-in-the-loop
approval before writing. Also implemented standalone examples of the Supervisor pattern
and Debate/Reflection pattern to understand all three coordination approaches.

---

## 1. Why One Agent Isn't Always Enough

A single agent doing everything is like one person researching, writing, editing, and
publishing an article simultaneously — constant context switching, lower quality.

Two concrete problems with single agents on complex tasks:

**Specialization** — an agent prompted to "research and write" splits its attention.
An agent prompted only to "research" gets very good at that specific task.

**Context window bloat** — a single agent on a long task accumulates a huge message
history. Every tool call, every result, every reasoning step goes into the same context.
Splitting work across agents means each one operates with a focused, smaller context.

---

## 2. The Three Multi-Agent Patterns

### Pipeline Pattern
Agents arranged in a fixed sequence. Each agent takes the previous one's output
as input and adds something to it.

```
[Researcher] → [Writer] → [END]
```

- Simple and predictable
- No going back — can't redo a previous step
- Best when steps are clearly sequential and independent

### Supervisor Pattern
One coordinator agent, multiple worker agents. The supervisor reads the task,
decides which specialist to call and in what order, then routes back to itself
after each worker finishes to decide what's still needed.

```
[Supervisor] → [Researcher] → [Supervisor] → [Summarizer] → [Supervisor] → END
```

- Flexible — supervisor can call workers in any order
- Can call the same worker multiple times
- Supervisor decides when the task is truly complete
- Best when task decomposition isn't known in advance

**Key implementation detail:** every worker goes back to the supervisor after
finishing, not directly to the next worker. The supervisor always controls routing.

```python
graph.add_edge("researcher", "supervisor")   # back to supervisor, not to summarizer
graph.add_edge("summarizer", "supervisor")   # back to supervisor
graph.add_conditional_edges("supervisor", route, {"researcher": "researcher", "summarizer": "summarizer", "done": END})
```

### Debate/Reflection Pattern
One agent generates output. A second agent critiques it. The first agent revises
based on the critique. Cycles repeat until quality is good enough or max iterations hit.

```
[Generator] → [Critic] → [Generator] → [Critic] → ... → END
```

- Self-improving — each revision incorporates feedback
- Stops after N iterations (max_iterations safety limit)
- Best for creative or quality-sensitive tasks (writing, code review, analysis)

**Key implementation detail:** `iteration` counter in state tracks how many rounds
have happened. Conditional edge after generator checks if limit is hit.

```python
def should_continue(state) -> str:
    if state["iteration"] >= state["max_iterations"]:
        return "done"
    return "continue"
```

---

## 3. How Agents Communicate — Shared State

Agents never talk to each other directly. They communicate through a shared
state dictionary that flows through the entire graph.

```python
class MultiAgentState(TypedDict):
    task: str                              # original user request
    research_results: str                  # researcher writes here
    final_article: str                     # writer reads research, writes here
    messages: Annotated[list, operator.add] # shared log
```

Researcher writes to `research_results`. Writer reads `research_results`.
That's the entire handoff — one field in a dictionary.

**Each agent builds its own fresh `messages` list** for its LLM calls.
`state["messages"]` is the shared log, not the agent's working context.
This is a critical distinction:

```python
# WRONG — sending the shared log as the agent's prompt
response = chat(messages=state["messages"], ...)

# CORRECT — building fresh messages with system prompt + task
messages = [
    {"role": "system", "content": "You are a researcher..."},
    {"role": "user", "content": f"Research: {state['task']}"}
]
response = chat(messages=messages, ...)
```

---

## 4. The 2-Agent Pipeline — Full Implementation

```python
def researcher_node(state: MultiAgentState) -> MultiAgentState:
    task = state["task"]
    messages = [
        {"role": "system", "content": "You are a research specialist. Search the web for information. Return structured findings. Do not write articles."},
        {"role": "user", "content": f"Research this topic thoroughly: {task}"}
    ]
    while True:
        response = chat(model="qwen3:8b", messages=messages, tools=tools)
        message = response["message"]
        messages.append(message)

        if message.get("tool_calls"):
            for tool_call in message["tool_calls"]:
                if tool_call["function"]["name"] == "web_search":
                    result = web_search(tool_call["function"]["arguments"]["query"])
                    messages.append({"role": "tool", "content": result})
        else:
            research = message["content"]
            break

    print(f"[Researcher] Done. Found {len(research)} chars.")
    return {
        "research_results": research,
        "messages": [{"role": "assistant", "content": f"Research complete: {research[:100]}..."}]
    }


def writer_node(state: MultiAgentState) -> MultiAgentState:
    messages = [
        {"role": "system", "content": "You are a professional writer. Write a clear, well-structured article from the research provided. Do not search for more information."},
        {"role": "user", "content": f"Task: {state['task']}\n\nResearch:\n{state['research_results']}\n\nWrite a well-structured article."}
    ]
    response = chat(model="qwen3:8b", messages=messages)  # no tools
    article = response["message"]["content"]

    print(f"[Writer] Done. Article is {len(article)} chars.")
    return {
        "final_article": article,
        "messages": [{"role": "assistant", "content": f"Article written: {article[:100]}..."}]
    }
```

**Why writer has no tools:** the writer's only job is to synthesize and write.
Giving it tools would let it go off and search more, defeating the specialization.
File saving happens after `invoke()` returns — not inside any agent node.

---

## 5. Human-in-the-Loop Before Writing

Added `interrupt_before=["write"]` so a human can review the research before
the writer produces an article from it. Catches bad research early (wrong topic,
insufficient findings) before wasting the writer's call.

```python
app = graph.compile(
    checkpointer=checkpointer,
    interrupt_before=["write"]
)

# Run until pause (after researcher, before writer)
app.invoke({"task": task, ...}, config=config)

# Show human the research
state = app.get_state(config)
print(state.values["research_results"])

approval = input("Approve research? (yes/no): ")
if approval == "yes":
    result = app.invoke(None, config=config)   # resume
else:
    print("Cancelled.")
```

---

## 6. Supervisor Pattern — Key Code

```python
def supervisor_node(state):
    if not state.get("research"):
        decision = "researcher"
    elif not state.get("summary"):
        decision = "summarizer"
    else:
        decision = "done"
    return {"next_agent": decision}

# Workers always return to supervisor
graph.add_edge("researcher", "supervisor")
graph.add_edge("summarizer", "supervisor")
graph.add_conditional_edges("supervisor", lambda s: s["next_agent"],
    {"researcher": "researcher", "summarizer": "summarizer", "done": END})
```

The `next_agent` field in state is how the supervisor communicates its decision
to the conditional edge router.

---

## 7. Debate/Reflection Pattern — Key Code

```python
class DebateState(TypedDict):
    task: str
    draft: str
    feedback: str
    iteration: int
    max_iterations: int

def generator_node(state):
    if not state["draft"]:
        prompt = f"Write about: {state['task']}"
    else:
        prompt = f"Rewrite incorporating this feedback:\n{state['feedback']}\n\nOriginal:\n{state['draft']}"
    # ... chat call ...
    return {"draft": new_draft, "iteration": state["iteration"] + 1}

def critic_node(state):
    # ... reviews state["draft"], returns feedback ...
    return {"feedback": feedback}

# Cycle: generator → critic → generator → ... → END
graph.add_conditional_edges("generator", should_continue,
    {"continue": "critic", "done": END})
graph.add_edge("critic", "generator")
```

---

## 8. Pattern Comparison

| | Pipeline | Supervisor | Debate/Reflection |
|---|---|---|---|
| Flow | Fixed sequence | Dynamic, supervisor decides | Cyclic loop |
| Can repeat a step | No | Yes | Yes (same two nodes) |
| Complexity | Low | Medium | Medium |
| Best for | Clear sequential tasks | Tasks where steps are unknown upfront | Quality-sensitive output |
| Stopping condition | Reaches END naturally | Supervisor says "done" | Max iterations hit |

---

## 9. When Multi-Agent is Overkill

| Use multi-agent when | Skip it when |
|---|---|
| Task naturally breaks into distinct specializations | One agent handles it cleanly |
| Single agent context gets overloaded | A few tool calls is all it needs |
| Quality improves from a separate reviewer | Coordination overhead > benefit |
| Steps depend on each other's outputs | Steps are independent |
| You need parallel execution | Sequential is fine |

Your Day 29 research agent (single agent, searched + wrote in one) was perfectly fine
for simple tasks. Multi-agent only pays off when complexity genuinely demands it.
