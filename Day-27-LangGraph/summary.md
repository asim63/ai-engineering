# Day 30 — LangGraph: Reliable Agent Workflows

## What I Built Today
Rebuilt yesterday's raw-loop research agent as a LangGraph state machine, added SQLite
checkpointing for persistent memory across script restarts, and implemented human-in-the-loop
approval before any file write — plus LangSmith tracing for observability.

---

## 1. Why Raw Agent Loops Get Fragile

Yesterday's agent worked, but everything lived inside one `while True` loop with nested
`if/elif` branching for tool routing, drift correction, and stopping conditions. As you add
more behavior — retries, approvals, branching logic — that loop turns into an unreadable
tangle of conditions. There's no clear structure, just one big function doing everything.

---

## 2. What LangGraph Is

A framework for building agent workflows as **graphs** instead of loops.

| Concept | What it is |
|---|---|
| **Node** | A function that does something (call LLM, run a tool, ask for approval) |
| **Edge** | A connection saying "after this node, go to that node" |
| **State** | A shared dictionary that flows through every node; each node reads and updates it |

```
   [START]
      │
      ▼
  ┌────────┐
  │ Node A  │ ← reads state, does something, updates state
  └────────┘
      │
      ▼
  ┌────────┐
  │ Node B  │
  └────────┘
      │
      ▼
   [END]
```

Each step is its own named function, and connections between them are explicit —
instead of buried inside nested conditionals.

---

## 3. Building State

State is defined with `TypedDict` — just describes what data flows through the graph.

```python
from typing import TypedDict, Annotated
import operator

class AgentState(TypedDict):
    messages: Annotated[list, operator.add]
```

**`Annotated[Type, metadata]`** — attaches extra metadata to a type hint without changing
the type itself. Here it says "messages is a list, AND here's extra info LangGraph should use."

**`operator.add`** — Python's `+` as a function. For lists, `+` means concatenate. Telling
LangGraph `Annotated[list, operator.add]` means: "when a node returns a new value for
`messages`, don't overwrite — append it onto the existing list." This replaces manual
`messages.append(...)` calls from yesterday's code.

**Important:** nodes must wrap a single new item in a list before returning it
(`{"messages": [message]}`), because `operator.add` concatenates lists — it can't
concatenate a list with a bare dict.

---

## 4. Nodes — Just Functions

```python
def agent_node(state: AgentState) -> AgentState:
    response = chat(model="qwen3:8b", messages=state['messages'], tools=tools)
    message = response['message']
    return {"messages": [message]}   # only return what changed


def tools_node(state: AgentState) -> AgentState:
    last_message = state["messages"][-1]
    tool_results = []
    for tool_call in last_message.get("tool_calls", []):
        tool_name = tool_call["function"]["name"]
        tool_args = tool_call["function"]["arguments"]
        result = route_tool(tool_name, tool_args)
        tool_results.append({"role": "tool", "content": result})
    return {"messages": tool_results}
```

A node only returns the keys it's changing — LangGraph automatically merges the return
value into the existing state using the schema's annotation rules.

**LangGraph manages the flow. Plain Python (`route_tool`) still has to map a tool name
to the actual function that runs.** LangGraph doesn't replace this — it has no idea what
`web_search` or `read_file` even are. There is a built-in `ToolNode` helper for this, but
it requires LangChain-style `Tool` objects, not raw Ollama dictionaries — writing
`route_tool` by hand kept things at a lower, more understandable level.

---

## 5. Conditional Edges

Instead of always going A → B → C, the graph decides the next node based on state.

```python
def should_continue(state: AgentState) -> str:
    last_message = state["messages"][-1]
    if last_message.get("tool_calls"):
        return "continue"
    return "end"

graph.add_conditional_edges(
    "agent",            # after this node finishes...
    should_continue,    # ...call this function to decide what's next...
    {
        "continue": "tools",   # if it returns "continue" → go to node "tools"
        "end": END              # if it returns "end" → stop
    }
)
```

**Key clarification:** the first argument to `add_node` is just a string label —
not the function name. `add_node("check", check_node)` means "register a node called
`check` that runs `check_node`." Every later reference (`set_entry_point`, `add_edge`,
conditional mappings) uses the string label, never the function itself.

The router function's return value is just a label — the dictionary maps that label
to the real node name to jump to. They can be different strings; they only look the
same here for readability.

---

## 6. How State Actually Transfers Between Nodes

LangGraph manages a single state dictionary internally and threads it through every
node call automatically:

```
state = {}                              ← starts as invoke() input
      │
node1(state) → returns partial update → merged into state
      │
node2(state) → receives FULL updated state → returns partial update → merged
      │
node3(state) → receives FULL updated state → returns partial update → merged
      │
END → returns final accumulated state
```

Every node sees everything accumulated so far but only needs to return what it's
adding or changing — merging happens automatically based on the `TypedDict` schema.

---

## 7. Rebuilding the Research Agent as a Graph

```python
graph = StateGraph(AgentState)
graph.add_node("agent", agent_node)
graph.add_node("tools", tools_node)
graph.set_entry_point("agent")
graph.add_conditional_edges("agent", should_continue, {"continue": "tools", "end": END})
graph.add_edge("tools", "agent")   # ← the loop: tools always goes back to agent
app = graph.compile()
```

```
   [START]
      │
      ▼
  ┌──────────┐
  │  agent    │ ← calls LLM, decides what to do
  └──────────┘
      │
   conditional: tool_calls present?
      │
   ┌──┴───┐
   ▼      ▼
 [tools] [END]
   │
   └──→ back to [agent]   ← the ReAct cycle, expressed as a graph cycle
```

`add_edge("tools", "agent")` is what creates the loop — same behavior as yesterday's
`while True`, just expressed as a graph cycle instead of a Python loop.

**Decision made:** the `done` tool was removed entirely. `should_continue` already stops
the graph whenever the model responds with plain text (no `tool_calls`) — qwen3 naturally
drifts to plain text when finished, so this matches its real behavior instead of fighting it.

---

## 8. Checkpointing — Persistent State

Without checkpointing, all progress lives only in memory and is lost if the script
crashes or restarts. Checkpointing saves state after every node runs.

```python
from langgraph.checkpoint.sqlite import SqliteSaver
import sqlite3

conn = sqlite3.connect("agent_checkpoints.db", check_same_thread=False)
checkpointer = SqliteSaver(conn)

app = graph.compile(checkpointer=checkpointer)
```

Every invocation needs a `thread_id` — how LangGraph knows which conversation to
save/resume:

```python
config = {"configurable": {"thread_id": "task-1"}}
result = app.invoke({"messages": [...]}, config=config)
```

**Tested:** ran the script once, asked "What is 25 * 48?" → got 1200. Closed the script
entirely. Ran it again as a brand new process with the same `thread_id`, asked
"Now subtract 500 from it" → the model correctly resolved "it" to 1200 from the
previous run and answered 700. No in-memory state existed between runs — everything
came from the SQLite file.

`thread_id` is what separates one user's conversation from another's in production —
different `thread_id` = completely isolated state.

---

## 9. Human-in-the-Loop

Pausing the graph before a risky action, showing what's about to happen, waiting for
approval, then proceeding or cancelling.

```python
app = graph.compile(
    checkpointer=checkpointer,
    interrupt_before=["tools"]   # pause right before this node runs
)
```

**Requires a checkpointer** — pausing and resuming needs LangGraph to save state
somewhere between the pause and the resume call. `MemorySaver` (RAM only) works fine
for resuming within the same script run; `SqliteSaver` is needed for resuming across
restarts.

```python
config = {"configurable": {"thread_id": "approval-test-1"}}
app.invoke({"messages": [...]}, config=config)   # runs until the interrupt

state = app.get_state(config)
while state.next:   # non-empty = graph is paused
    last_message = state.values["messages"][-1]
    tool_calls = last_message.get("tool_calls", [])

    for tool_call in tool_calls:
        if tool_call["function"]["name"] == "write_file":
            args = tool_call["function"]["arguments"]
            print(f"APPROVAL NEEDED: write_file → {args.get('filepath')}")
            approval = input("Approve? (yes/no): ").strip().lower()

            if approval != "yes":
                print("Cancelled.")
                return state.values   # return current state, not None

    result = app.invoke(None, config=config)   # None = resume from checkpoint
    state = app.get_state(config)

return state.values
```

**Key concept:** `app.invoke(None, config=config)` — passing `None` tells LangGraph
"don't start fresh, resume from the saved checkpoint." This only works because of the
checkpointer — human-in-the-loop and checkpointing are connected concepts.

**Tested both paths:** approved a write → file was created. Rejected a write →
`write_file` never executed, graph stopped cleanly.

---

## 10. LangSmith — Observability

A web dashboard showing a visual trace of every node hit, every LLM call, every tool
result — instead of reading terminal prints.

```
LANGCHAIN_TRACING_V2=true
LANGCHAIN_API_KEY=your_key_here
LANGCHAIN_PROJECT=day27-langgraph
```

```python
import os
os.environ["LANGCHAIN_TRACING_V2"] = os.getenv("LANGCHAIN_TRACING_V2")
os.environ["LANGCHAIN_API_KEY"] = os.getenv("LANGCHAIN_API_KEY")
os.environ["LANGCHAIN_PROJECT"] = os.getenv("LANGCHAIN_PROJECT")
```

No changes to the graph itself — LangGraph automatically reports to LangSmith once
these environment variables are set. Becomes essential once agents get complex enough
that print statements aren't enough to debug what's happening.

