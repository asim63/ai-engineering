from langgraph.graph import StateGraph, END
from typing import TypedDict, Annotated
import operator
from ollama import chat
from tavily import TavilyClient
from dotenv import load_dotenv
import os, math


load_dotenv()
tools=[
    {
        "type":"function",
        "function":{
            "name":"web_search",
            "description": "Search the web for current information on any topic. Use this when you need to find information you dont already know.",
            "parameters":{
                "type":"object",
                "properties":{
                    "query":{
                        "type":"string",
                        "description": "The search query. Be specific for better results."
                    }
                },
                "required":["query"]
            }
        }
    },
    {
        "type":"function",
        "function":{
            "name":"read_file",
            "description":"Read the contents of the file from the local filesystem.",
            "parameters":{
                "type":"object",
                "properties":{
                    "filepath": {
                        "type": "string",
                        "description":r"The path to the file to read. Examples: Day-27-LangGraph\notes.txt or Day-26-Building-Agent\data.md"
                    }
                },
                "required": ["filepath"]
            }
        }
    },
    {
        "type":"function",
        "function":{
            "name":"write_file",
            "description":"Write content to a file on the local filesystem. Creates the file if if doesnt exist, overwrite if it does exist.",
            "parameters":{
                "type":"object",
                "properties":{
                    "filepath":{
                        "type":"string",
                        "description":r"The path to the file to write. Example:  Day-27-LangGraph\notes.txt or Day-26-Building-Agent\data.md "
                    },
                    "content":{
                        "type":"string",
                        "description":"The content to write into the file"
                    }
                },
                "required": ["filepath","content"]
            }
        }
    },
    {
        "type":"function",
        "function":{
            "name":"calculate",
            "description":"Performs arithmetic operation, Use this for ANY math operation instead of calculating by yourself.",
            "parameters":{
                "type":"object",
                "properties":{
                    "expression":{
                        "type":"string",
                        "description":"The math expression to evaluate. Examples: '23*234', '100/3"
                    }
                },
                "required":["expression"]
            }
        }
    }
    ]
tavilyClient = TavilyClient(api_key=os.getenv("Tavily_API_Key"))

def web_search(query: str)-> str:
    try:
        results = tavilyClient.search(query = query, max_results=3)
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
        with open(filepath, "r", encoding="utf-8") as file:
            return file.read()
    except FileNotFoundError:
        return f"Error: File '{filepath} not found"
    except Exception as e:
        return f"Error occured: {e}"

def write_file(filepath: str, content: str) -> str:
    try:
        with open(filepath, "w", encoding="utf-8") as file:
            file.write(content)
            return f"Written to {filepath} successfully."
    except Exception as e:
        return f"Error occured: {e}"
    
def calculate(expression: str) -> str:
    try: 
        result = eval(
            expression,
            {"__builtins__":{}},
            {"sqrt":math.sqrt, "pow": pow, "abs": abs, "round":round}
        )
        return str(result)
    except Exception as e:
        return f"Error occured in calculate: {e}"

def route_tool(tool_name: str, tool_args: dict) -> str:
    print(f"[Tool] {tool_name} called with {tool_args}")
    if tool_name == "web_search":
        result = web_search(tool_args["query"])
    elif tool_name == "read_file":
        result = read_file(tool_args["filepath"])
    elif tool_name == "write_file":
        result = write_file(tool_args["filepath"], tool_args["content"])
    elif tool_name == "calculate":
        result = calculate(tool_args["expression"])
    else:
        result = f"Error: Unknown tool '{tool_name}'"
    
    print(f"[Result] {result[:100]}")
    return result


class AgentState(TypedDict):
    messages: Annotated[list,operator.add] # this operator.add is required to tell while merging dont overwrite the message but instead concatanate.
    
def agent_node(state: AgentState) -> AgentState:
    response = chat(
        model="qwen3:8b",
        messages=state['messages'],
        tools = tools
    )
    message = response['message']
    return {"messages":[message]}

def tools_node(state: AgentState) -> AgentState:
    last_message = state["messages"][-1]
    tool_results = []
    
    for tool_call in last_message.get("tool_calls", []):
        tool_name = tool_call["function"]["name"]
        tool_args = tool_call["function"]["arguments"]
        result = route_tool(tool_name= tool_name, tool_args= tool_args)
        tool_results.append({"role":"tool","content":result})
    return {"messages": tool_results}

def should_continue(state: AgentState) -> str:
    last_message = state["messages"][-1]
    if last_message.get("tool_calls"):
        return "continue"
    return "end"
graph = StateGraph(AgentState)

graph.add_node("agent",agent_node)
graph.add_node("tools",tools_node)

graph.set_entry_point("agent")
graph.add_conditional_edges(
    "agent",
    should_continue,
    {
        "continue":"tools",
        "end": END
    }
)
graph.add_edge("tools","agent")
app = graph.compile()

if __name__ == "__main__":
    result = app.invoke({
        "messages": [
            {"role": "user", "content": "What is 25 * 48?"}
        ]
    })

    print("\n" + "="*50)
    print("FULL MESSAGE HISTORY")
    print("="*50)
    for msg in result["messages"]:
        print(msg)

    print("\n" + "="*50)
    print("FINAL ANSWER")
    print("="*50)
    print(result["messages"][-1]["content"])