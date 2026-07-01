from langgraph.graph import StateGraph, END
from langgraph.checkpoint.memory import MemorySaver
from typing import TypedDict, Annotated
import operator
class State(TypedDict):
    messages: Annotated[list, operator.add]

def risky_node(state: State) -> State:
    print("[RISKY ACTION] This is the dangerous step that needs approval.")
    return {"messages": ["risky action completed"]}


def safe_node(state: State) -> State:
    print("[SAFE] This always runs without approval.")
    return {"messages": ["safe action completed"]}


# ── Build graph ──────────────────────────────
graph = StateGraph(State)
graph.add_node("safe", safe_node)
graph.add_node("risky", risky_node)

graph.set_entry_point("safe")
graph.add_edge("safe", "risky")
graph.add_edge("risky", END)

checkpointer = MemorySaver()   # in-memory, simplest option

app = graph.compile(
    checkpointer=checkpointer,
    interrupt_before=["risky"]   # pause right before "risky" runs
)

# ── Run it ──────────────────────────────
config = {"configurable": {"thread_id": "demo-1"}}

print("Starting graph...")
app.invoke({"messages": []}, config=config)

# At this point, the graph has paused BEFORE "risky" ran
print("\nGraph is paused. Asking for approval...")
approval = input("Approve the risky action? (yes/no): ").strip().lower()

if approval == "yes":
    print("\nResuming graph...")
    result = app.invoke(None, config=config)   # None = resume from pause
    print("\nFinal messages:", result["messages"])
else:
    print("\nCancelled. Risky node never ran.")