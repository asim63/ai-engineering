from ollama import chat
from langgraph.graph import StateGraph, END
from typing import Annotated, TypedDict
from tavily import TavilyClient
from dotenv import load_dotenv
from langgraph.checkpoint.sqlite import SqliteSaver
import sqlite3
import os
import operator
import requests
from bs4 import BeautifulSoup

load_dotenv()
tavilyClient = TavilyClient(api_key=os.getenv("Tavily_API_Key"))
conn = sqlite3.connect(r"Day-29-Project4\agent_checkpoint.db", check_same_thread=False)
checkpointer = SqliteSaver(conn)

tools = [
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
        "type": "function",
        "function": {
            "name": "fetch_url",
            "description": "Fetch the raw content of a specific URL. Use this when you want to get more details from a specific webpage found in search results.",
            "parameters": {
                "type": "object",
                "properties": {
                    "url": {
                        "type": "string",
                        "description": "The full URL to fetch. Example: 'https://example.com/article'"
                    }
                },
                "required": ["url"]
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "extract_text_from_url",
            "description": "Fetch a URL and extract clean readable text, removing HTML tags, navigation, and ads. Better than fetch_url for reading article content.",
            "parameters": {
                "type": "object",
                "properties": {
                    "url": {
                        "type": "string",
                        "description": "The full URL to extract text from."
                    }
                },
                "required": ["url"]
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "summarize_text",
            "description": "Summarize a long piece of text into key points. Use this when fetched content is too long to process directly.",
            "parameters": {
                "type": "object",
                "properties": {
                    "text": {
                        "type": "string",
                        "description": "The text to summarize."
                    }
                },
                "required": ["text"]
            }
        }
    }
]

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
        return f"Error: File '{filepath}' not found"
    except Exception as e:
        return f"Error occured: {e}"

def write_file(filepath: str, content: str) -> str:
    try:
        with open(filepath, "w", encoding="utf-8") as file:
            file.write(content)
            return f"Written to {filepath} successfully."
    except Exception as e:
        return f"Error occured: {e}"
    
def route_tool(tool_name: str, tool_args: dict) -> str:
    print(f"[Tool] {tool_name} called with {tool_args}")
    if tool_name == "web_search":
        result = web_search(tool_args["query"])
    elif tool_name == "read_file":
        result = read_file(tool_args["filepath"])
    elif tool_name == "write_file":
        result = write_file(tool_args["filepath"], tool_args["content"])
    elif tool_name == "fetch_url":
        result = fetch_url(tool_args["url"])
    elif tool_name == "extract_text_from_url":
        result = extract_text_from_url(tool_args["url"])
    elif tool_name == "summarize_text":
        result = summarize_text(tool_args["text"])
    else:
        result = f"Error: Unknown tool '{tool_name}'"
    
    print(f"[Result] {result[:100]}")
    return result

def fetch_url(url:str) -> str:
    try:
        headers = {"User-Agent":"Mozilla/5.0"}
        response = requests.get(url, headers=headers, timeout=10)
        response.raise_for_status()
        return response.text[:5000]
    except Exception as e:
        return f"Error occured : {e}"

def extract_text_from_url(url: str) -> str:
    try:
        headers = {"User-Agent": "Mozilla/5.0"}
        response = requests.get(url, headers=headers, timeout=10)
        soup = BeautifulSoup(response.text, "html.parser")

        # Remove script and style tags — they're never useful
        for tag in soup(["script", "style", "nav", "footer", "header","aside","noscript"]):
            tag.decompose()

        text = soup.get_text(separator="\n")
        # Clean up excessive whitespace
        lines = [line.strip() for line in text.splitlines() if line.strip()]
        clean_text = "\n".join(lines)
        return clean_text[:5000]  # limit to 5000 chars so we don't explode context
    except Exception as e:
        return f"Error extracting text: {e}"
    
def summarize_text(text: str) -> str:
    try:
        response = chat(
            model="qwen3:8b",
            messages=[
                {"role": "system", "content": "You are a summarizer. Extract the key facts and main points from the provided text. Be concise."},
                {"role": "user", "content": f"Summarize this text into key points:\n\n{text}"}
            ]
        )
        raw = response["message"]["content"]
        if "<think>" in raw:
            raw = raw[raw.rfind("</think>") + 8:].strip()
        return raw
    except Exception as e:
        return f"Error summarizing: {e}"

class AgentState(TypedDict):
    task: str
    plan: str
    research: str
    gaps: str
    final_report: str
    review_iteration: int
    messages: Annotated[list,operator.add] # this operator.add is required to tell while merging dont overwrite the message but instead concatanate.
    
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

def planner_node(state: AgentState) -> AgentState:
    task = state['task']
    response = chat(
        model="qwen3:8b",
        messages=[
            {
            "role":"system",
            "content":"You are a research planner. Give a research task, create a structured research plan. List 3-5 specific search queries to run, in order of priority. Do NOT search yet — only plan. "
        },
        {
                "role": "user",
                "content": f"Create a research plan for this task: {task}"
        }
        ]
    )
    raw = response["message"]["content"]
    if "<think>" in raw:
        raw = raw[raw.rfind("</think>") + 8:].strip()
    
    print(f"[PLANNER] Plan created:\n{raw[:200]}...")
    return {
        "plan": raw,
        "messages": [{"role": "assistant", "content": f"Plan: {raw[:100]}..."}]
    }
def researcher_node(state: AgentState) -> AgentState:
    task = state["task"]
    plan = state["plan"]
    previous_research = state.get("research", "")
    gaps = state.get("gaps", "")

    # Tell it about the plan AND any gaps from reviewer
    user_content = f"Task: {task}\n\nResearch Plan:\n{plan}"
    if gaps:
        user_content += f"\n\nThe reviewer identified these gaps — focus on filling them:\n{gaps}"
    if previous_research:
        user_content += f"\n\nResearch so far (don't repeat this):\n{previous_research[:500]}..."

    messages = [
        {
            "role": "system",
            "content": "You are a research specialist. Follow the research plan and use your tools to gather information. Use web_search for finding information, extract_text_from_url to get full content from promising URLs, and summarize_text for long content. Be thorough."
        },
        {
            "role": "user",
            "content": user_content
        }
    ]

    while True:
        response = chat(model="qwen3:8b", messages=messages, tools=tools)
        message = response["message"]
        messages.append(message)

        if message.get("tool_calls"):
            for tool_call in message["tool_calls"]:
                tool_name = tool_call["function"]["name"]
                tool_args = tool_call["function"]["arguments"]
                result = route_tool(tool_name, tool_args)
                messages.append({"role": "tool", "content": result})
        else:
            research = message["content"]
            if "<think>" in research:
                research = research[research.rfind("</think>") + 8:].strip()
            break

    # Append to existing research, don't overwrite
    combined = previous_research + "\n\n" + research if previous_research else research

    print(f"[RESEARCHER] Done. Total research: {len(combined)} chars.")
    return {
        "research": combined,
        "messages": [{"role": "assistant", "content": f"Research: {research[:100]}..."}]
    }
def reviewer_node(state: AgentState) -> AgentState:
    response = chat(
        model="qwen3:8b",
        messages=[
            {
                "role": "system",
                "content": """You are a research reviewer. Read the research and decide if it's sufficient.
If sufficient: respond with APPROVED followed by a brief note.
If gaps exist: respond with GAPS FOUND followed by specific missing information."""
            },
            {
                "role": "user",
                "content": f"Task: {state['task']}\n\nResearch collected:\n{state['research']}\n\nIs this research sufficient to write a complete report?"
            }
        ]
    )
    feedback = response["message"]["content"]
    if "<think>" in feedback:
        feedback = feedback[feedback.rfind("</think>") + 8:].strip()

    iteration = state.get("review_iteration", 0) + 1
    print(f"[REVIEWER] Iteration {iteration}: {feedback[:100]}...")

    return {
        "gaps": feedback,
        "review_iteration": iteration,
        "messages": [{"role": "assistant", "content": f"Review: {feedback[:100]}..."}]
    }


def should_continue_research(state: AgentState) -> str:
    gaps = state.get("gaps", "")
    iteration = state.get("review_iteration", 0)

    # Safety limit — max 2 review loops
    if iteration >= 2:
        return "format"

    if "APPROVED" in gaps.upper():
        return "format"
    else:
        return "research"   # loop back to researcher
    
def formatter_node(state: AgentState) -> AgentState:
    response = chat(
        model="qwen3:8b",
        messages=[
            {
                "role": "system",
                "content": "You are a professional report writer. Format the research into a clean, well-structured markdown report with proper headings, sections, and a summary. Make it readable and comprehensive."
            },
            {
                "role": "user",
                "content": f"Task: {state['task']}\n\nResearch:\n{state['research']}\n\nWrite a complete markdown report."
            }
        ]
    )
    report = response["message"]["content"]
    if "<think>" in report:
        report = report[report.rfind("</think>") + 8:].strip()

    print(f"[FORMATTER] Report ready. {len(report)} chars.")
    return {
        "final_report": report,
        "messages": [{"role": "assistant", "content": f"Report: {report[:100]}..."}]
    }    

graph = StateGraph(AgentState)

graph.add_node("planner", planner_node)
graph.add_node("researcher", researcher_node)
graph.add_node("tools", tools_node)
graph.add_node("reviewer", reviewer_node)
graph.add_node("formatter", formatter_node)

graph.set_entry_point("planner")

# Planner always goes to researcher
graph.add_edge("planner", "researcher")

# Researcher ↔ tools loop (same as before)
graph.add_conditional_edges(
    "researcher",
    should_continue,        # your existing function checking tool_calls
    {
        "continue": "tools",
        "end": "reviewer"   # when researcher is done → go to reviewer
    }
)
graph.add_edge("tools", "researcher")

# Reviewer decides: loop back or format
graph.add_conditional_edges(
    "reviewer",
    should_continue_research,
    {
        "research": "researcher",   # gaps found → back to researcher
        "format": "formatter"       # approved → format
    }
)

graph.add_edge("formatter", END)

app = graph.compile(checkpointer=checkpointer)

if __name__ == "__main__":
    import uuid
    config = {"configurable": {"thread_id": str(uuid.uuid4())}}

    result = app.invoke(
        {
            "task": "What are the latest developments in quantum computing in 2025?",
            "plan": "",
            "research": "",
            "gaps": "",
            "final_report": "",
            "review_iteration": 0,
            "messages": []
        },
        config=config
    )

    print("\n" + "="*60)
    print("FINAL REPORT")
    print("="*60)
    print(result["final_report"])

    # Save to file
    with open(r"D:\Projects\ai-engineering\Day-29-Project4\report.md", "w", encoding="utf-8") as f:
        f.write(result["final_report"])
    print("\nReport saved to report.md")