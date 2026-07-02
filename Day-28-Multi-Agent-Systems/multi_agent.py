from tavily import TavilyClient
from dotenv import load_dotenv
from langgraph.graph import StateGraph, END
import os
from langgraph.checkpoint.sqlite import SqliteSaver
from ollama import chat
from typing import TypedDict, Annotated
import sqlite3
import operator

load_dotenv()
tavily_client = TavilyClient(api_key=os.getenv("Tavily_API_Key"))

conn = sqlite3.connect(r"Day-28-Multi-Agent-Systems\agent_checkpoints.db",check_same_thread= False)
checkpointer = SqliteSaver(conn)
tools = [
    {
        "type": "function",
        "function":{
            "name":"web_search",
            "description":"Search the web for current information on any topic. Use this when you need to find information you dont already know.",
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
    # {
    #     "type":"function",
    #     "function":{
    #         "name":"write_file",
    #         "description":"Write content to a file on the local filesystem. Creates the file if if doesnt exist, overwrite if it does exist.",
    #         "parameters":{
    #             "type":"object",
    #             "properties":{
    #                 "filepath":{
    #                     "type":"string",
    #                     "description":r"The path to the file to write. Example:  Day-27-LangGraph\notes.txt or Day-26-Building-Agent\data.md "
    #                 },
    #                 "content":{
    #                     "type": "string",
    #                     "description":"The content to write into the file"
    #                 }
    #             },
    #             "required":["filepath","content"]
    #         }
    #     }
    # }
]

def web_search(query: str) -> str:
    try:
        results = tavily_client.search(query=query, max_results=3)
        output = ""
        for r in results["results"]:
            output += f"Title: {r['title']}\n"
            output += f"URL: {r['url']}\n"
            output += f"Content: {r['content']}\n"
            output += "-"*50 + "\n"
        return output
    except Exception as e:
        return f"Error occured during searching: {e}"
    
def write_file(filepath: str, content:str) -> str:
    try:
        with open(filepath, "w", encoding="utf-8") as file:
            file.write(content)
            return f"Written successfully into '{filepath}'"
    except Exception as e:
        return f"Error occured during write: {e}"
            
            
class MultiAgentState(TypedDict):
    task: str #this is the user request
    research_results: str #this is where the write reads from.
    final_article: str
    messages: Annotated[list, operator.add]
    
    
def researcher_node(state: MultiAgentState) -> MultiAgentState:
    task = state['task']
    messages = [
        {
            "role": "system",
            "content": "You are a research specialist. Search the web for information on the given topic. Return structured findings with key facts. Do not write articles, only gather and present information clearly."
        },
        {
            "role": "user",
            "content": f"Research this topic thoroughly: {task}"
        }
    ]
    while True:
        response = chat(
            model="qwen3:8b",
            messages= messages,
            tools= tools
        )
        message = response["message"]
        messages.append(message)
        
        if message.get("tool_calls"):
            for tool_call in message["tool_calls"]:
                tool_name = tool_call["function"]["name"]
                tool_args = tool_call["function"]["arguments"]
                if tool_name == "web_search":
                    result = web_search(tool_args["query"])
                    messages.append({"role":"tool","content":result})
        else:
            research = message["content"]
            break
    print(f"[Researcher] Done. Found {len(research)} chars of research.")
    return {
        "research_results": research,
        "messages":[{
            "role": "assistant",
            "content": f"Research complete : {research[:100]}..."
        }]
    }

def writer_node(state: MultiAgentState) -> MultiAgentState:
    research = state['research_results']   # read what researcher wrote
    task = state['task']                   # also read original task for context

    # Writer gets research as context in its prompt
    messages = [
        {
            "role": "system",
            "content": "You are a professional writer. Using the research provided, write a clear, well-structured article. Do not search for more information — only use what is given."
        },
        {
            "role": "user",
            "content": f"Original task: {task}\n\nResearch findings:\n{research}\n\nNow write a well-structured article based on this research."
        }
    ]

    response = chat(model="qwen3:8b", messages=messages)  # no tools needed for writer
    article = response["message"]["content"]

    print(f"[Writer] Done. Article is {len(article)} chars.")
    return {
        "final_article": article,
        "messages": [{"role": "assistant", "content": f"Article written: {article[:100]}..."}]
    }
   
    
graph = StateGraph(MultiAgentState)
graph.add_node("search",researcher_node)
graph.add_node("write",writer_node)
graph.set_entry_point("search")    
graph.add_edge("search","write")
graph.add_edge("write",END)

app = graph.compile(checkpointer=checkpointer)

config = {"configurable":{"thread_id":"multi-agent-1"}}

result = app.invoke({
    "task": "The latest football transfer reports in 2026",
    "research_results": "",
    "final_article": "",
    "messages": []
    },
    config = config
)
print("\n" + "="*50)
print("FINAL ARTICLE")
print("="*50)
print(result["final_article"])


with open(r"Day-28-Multi-Agent-Systems\final_article.md", "w", encoding="utf-8") as f:
    f.write(result["final_article"])
print("\nArticle saved to final_article.md")