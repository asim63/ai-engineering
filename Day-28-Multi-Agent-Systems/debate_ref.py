from langgraph.graph import StateGraph, END
from ollama import chat
from typing import TypedDict, Annotated
import operator

class DebateState(TypedDict):
    task: str
    draft: str
    feedback: str
    iteration: int           # track how many rounds of debate
    max_iterations: int
    final: str
    messages: Annotated[list, operator.add]

def generator_node(state: DebateState) -> DebateState:
    task = state["task"]
    feedback = state.get("feedback", "")
    draft = state.get("draft", "")
    iteration = state.get("iteration", 0)

    if not draft:
        # First draft — no feedback yet
        prompt = f"Write a short paragraph about: {task}"
    else:
        # Revision — incorporate critic's feedback
        prompt = f"""You wrote this draft:
{draft}

The critic said:
{feedback}

Rewrite the paragraph incorporating the feedback. Improve it."""

    response = chat(
        model="qwen3:8b",
        messages=[
            {"role": "system", "content": "You are a writer. Write clearly and concisely."},
            {"role": "user", "content": prompt}
        ]
    )
    new_draft = response["message"]["content"]
    print(f"[GENERATOR] Iteration {iteration + 1} draft ready.")

    return {
        "draft": new_draft,
        "iteration": iteration + 1,
        "messages": [{"role": "assistant", "content": f"Draft {iteration+1}: {new_draft[:100]}..."}]
    }

def critic_node(state: DebateState) -> DebateState:
    response = chat(
        model="qwen3:8b",
        messages=[
            {"role": "system", "content": "You are a strict editor. Give specific, actionable feedback on how to improve this writing. Be critical but constructive."},
            {"role": "user", "content": f"Review this paragraph and give feedback:\n{state['draft']}"}
        ]
    )
    feedback = response["message"]["content"]
    print(f"[CRITIC] Feedback ready.")
    return {
        "feedback": feedback,
        "messages": [{"role": "assistant", "content": f"Feedback: {feedback[:100]}..."}]
    }

def should_continue(state: DebateState) -> str:
    if state["iteration"] >= state["max_iterations"]:
        return "done"
    return "continue"

# Build graph
graph = StateGraph(DebateState)
graph.add_node("generator", generator_node)
graph.add_node("critic", critic_node)

graph.set_entry_point("generator")

# After generator — check if we should keep debating
graph.add_conditional_edges(
    "generator",
    should_continue,
    {
        "continue": "critic",   # keep going → critic reviews
        "done": END             # max iterations hit → stop
    }
)

# After critic — always go back to generator to revise
graph.add_edge("critic", "generator")

app = graph.compile()

result = app.invoke({
    "task": "Explain why sleep is important for learning",
    "draft": "",
    "feedback": "",
    "iteration": 0,
    "max_iterations": 3,    # ← 3 rounds of generate → critique → revise
    "final": "",
    "messages": []
})

print("\n" + "="*50)
print(f"FINAL DRAFT (after {result['iteration']} iterations)")
print("="*50)
print(result["draft"])