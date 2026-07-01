from langgraph.graph import StateGraph, END
from typing import TypedDict

class GraphState(TypedDict):
    number: int
    result: str

def check_node(state: GraphState)-> GraphState:
    print(f"Check number: {state['number']}")
    return state

def big_number_node(state: GraphState) -> GraphState:
    print("This is a big number!")
    return {"result": f"{state['number']} is BIG"}

def small_number_node(state: GraphState) -> GraphState:
    print("This is a small number!")
    return {"result": f"{state['number']} is small"}

def route_by_size(state: GraphState) -> str:
    if state["number"] > 100:
        return "big"
    else:
        return "small"
    
graph = StateGraph(GraphState)

graph.add_node("check",check_node)
graph.add_node("big",big_number_node)
graph.add_node("small", small_number_node)

graph.set_entry_point("check")

graph.add_conditional_edges(
    "check",
    route_by_size,
    {
        "big":"big",
        "small":"small"
    }
)
graph.add_edge("big", END)
graph.add_edge("small", END)

app = graph.compile()

result1 = app.invoke({"number": 500})
print(f"Result: {result1['result']}\n")

result2 = app.invoke({"number": 40})
print(f"Result: {result2['result']}\n")