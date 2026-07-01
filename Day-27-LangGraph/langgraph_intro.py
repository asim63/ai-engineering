from langgraph.graph import StateGraph, END
from typing import TypedDict

class GraphState(TypedDict):
    input_text: str
    processed_text: str
    output_text: str
    
    
#Node functions
def input_node(state: GraphState) -> GraphState:
    print(f"Received : {state['input_text']}")
    return state

def process_node(state: GraphState) -> GraphState:
    text = state['input_text']
    processed = text.upper()
    print(f"Processed : {processed}")
    return {"processed_text":processed}

def output_node(state: GraphState) -> GraphState:
    final = f"Final output: {state['processed_text']}"
    print(f"{final}")
    return {"output_text":final}

graph = StateGraph(GraphState)

graph.add_node("input",input_node)
graph.add_node("process",process_node)
graph.add_node("output",output_node)

graph.set_entry_point("input")
graph.add_edge("input","process")
graph.add_edge("process","output")
graph.add_edge("output", END)

app = graph.compile()

result = app.invoke({"input_text": "hello langgraph"})
print(f"\n Initial State : {result}")