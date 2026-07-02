from langgraph.graph import StateGraph, END
from ollama import chat
from typing import TypedDict, Annotated
import operator

class SupervisorState(TypedDict):
    task: str
    research: str
    summary: str
    final: str
    next_agent: str          # supervisor writes here to decide who runs next
    messages: Annotated[list, operator.add]

def supervisor_node(state: SupervisorState) -> SupervisorState:
    task = state["task"]
    research = state.get("research", "")
    summary = state.get("summary", "")

    # Supervisor decides what to do next based on current state
    if not research:
        decision = "researcher"
    elif not summary:
        decision = "summarizer"
    else:
        decision = "done"

    print(f"[SUPERVISOR] Decided: {decision}")
    return {
        "next_agent": decision,
        "messages": [{"role": "assistant", "content": f"Supervisor routing to: {decision}"}]
    }

def researcher_node(state: SupervisorState) -> SupervisorState:
    response = chat(
        model="qwen3:8b",
        messages=[
            {"role": "system", "content": "You are a researcher. Find key facts about the topic. Be concise."},
            {"role": "user", "content": f"Research this: {state['task']}"}
        ]
    )
    research = response["message"]["content"]
    print(f"[RESEARCHER] Done.")
    return {
        "research": research,
        "messages": [{"role": "assistant", "content": f"Research: {research[:100]}..."}]
    }

def summarizer_node(state: SupervisorState) -> SupervisorState:
    response = chat(
        model="qwen3:8b",
        messages=[
            {"role": "system", "content": "You are a summarizer. Create a brief executive summary."},
            {"role": "user", "content": f"Summarize this research into 3 bullet points:\n{state['research']}"}
        ]
    )
    summary = response["message"]["content"]
    print(f"[SUMMARIZER] Done.")
    return {
        "summary": summary,
        "final": summary,
        "messages": [{"role": "assistant", "content": f"Summary: {summary[:100]}..."}]
    }

# Router function for conditional edges
def route(state: SupervisorState) -> str:
    return state["next_agent"]

# Build graph
graph = StateGraph(SupervisorState)
graph.add_node("supervisor", supervisor_node)
graph.add_node("researcher", researcher_node)
graph.add_node("summarizer", summarizer_node)

graph.set_entry_point("supervisor")

# Supervisor decides where to go
graph.add_conditional_edges(
    "supervisor",
    route,
    {
        "researcher": "researcher",
        "summarizer": "summarizer",
        "done": END
    }
)

# After each worker, always go back to supervisor
graph.add_edge("researcher", "supervisor")
graph.add_edge("summarizer", "supervisor")

app = graph.compile()

result = app.invoke({
    "task": "How does photosynthesis work?",
    "research": "",
    "summary": "",
    "final": "",
    "next_agent": "",
    "messages": []
})

print("\n" + "="*50)
print("FINAL OUTPUT")
print("="*50)
print(result["final"])