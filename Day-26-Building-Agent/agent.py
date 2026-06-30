import math
import os
from dotenv import load_dotenv
from tavily import TavilyClient
from ollama import chat

load_dotenv()
tavily_client = TavilyClient(api_key= os.getenv("Tavily_API_Key"))

file_path = r"Day-26-Building-Agent\test.txt"

def web_search(query: str) -> str:
    try:
        results = tavily_client.search(query = query, max_results= 3)
        output = ""
        for r in results["results"]:
            output += f"Title: {r['title']}\n"
            output += f"URL: {r['url']}\n"
            output += f"Content: {r['content']}\n"
            output += "-" * 40 + "\n"
        return output
    except Exception as e:
        return f"Search error: {e}"

def read_file(filepath):
    try:
        with open(f"{filepath}", encoding="utf-8",mode="r") as file:
            content = file.read()
            return content
    except FileNotFoundError:
        return f"Error: File '{filepath}' not found."
    except Exception as e:
        return f"Error occured: {e}"
    
def write_file(filepath,content):
    try: 
        with open(f"{filepath}", encoding="utf-8",mode="w") as file:
            file.write(content)
            return f"Successfully written to '{filepath}'"
    except Exception as e:
        return f"Error occured: {e}"
        
def calculate(expression:str) -> str:
    try: 
        result=  eval(
            expression,
            {"__builtins__":{}},
            {"sqrt":math.sqrt, "pow":pow, "abs": abs, "round":round}
        )
        return str(result)
    except Exception as e:
        return f"Error occured: {e}"
    
    
# print(write_file(r"Day-26-Building-Agent\test.txt", "hello from agent"))
# print(read_file(r"Day-26-Building-Agent\test.txt"))
# print(calculate("99 * 11"))

# Writing Tools
tools = [
    {
        "type":"function",
        "function":{
            "name":"web_search",
            "description":"Search the web for current information on any topic. Use this when you need to find information you dont already know.",
            "parameters": {
                "type":"object",
                "properties":{
                    "query":{
                        "type":"string",
                        "description":"The search query. Be specific for better results."
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
                        "description":r"The path to the file to read. Examples: Day-26-Building-Agent\notes.txt or Day-26-Building-Agent\data.md"
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
                        "description":r"The path to the file to write. Example:  Day-26-Building-Agent\notes.txt or Day-26-Building-Agent\data.md "
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
    },
    {
        "type": "function",
        "function": {
            "name": "done",
            "description": "Call this when the task is fully complete and you have nothing left to do. Use this to signal that you are finished.",
            "parameters": {
                "type": "object",
                "properties": {
                    "summary": {
                        "type": "string",
                        "description": "A short summary of what you accomplished."
                    }
                },
                "required": ["summary"]
            }
        }
    }
]

def route_tool(tool_name:str, tool_args: dict) -> str:
    print(f"[Tool] {tool_name} called with {tool_args}")
    
    if tool_name == "web_search":
        result = web_search(tool_args["query"])
    elif tool_name == "read_file":
        result = read_file(tool_args["filepath"])
    elif tool_name == "write_file":
        result = write_file(tool_args["filepath"], tool_args["content"])
    elif tool_name == "calculate":
        result = calculate(tool_args["expression"])
    elif tool_name == "done":
        result = "DONE"
    else:
        result = f"Error: Unknown tool '{tool_name}'"
    
    print(f"[Result] {result[:100]}")
    return result

def run_agent(task:str, max_iterations: int = 10):
    os.chdir(r"D:\Projects\ai-engineering\Day-26-Building-Agent")
    print(f"\n{'-'*50}")
    print(f"Task: {task}")
    print(f"{'-'*50}")
    
    messages = [
        {
        "role": "system",
        "content": """You are a research agent with access to tools.
        IMPORTANT RULES:
        - Always use tools to complete tasks, never respond with plain text until done.
        - You MUST call the 'done' tool when the task is complete. 
        - Do NOT write <done> or any text. ONLY call the done tool.
        - Do NOT say 'let me know if you need anything'.
        - After getting a tool result that completes the task, immediately call done."""
        },
        {
            "role":"user",
            "content":task
        }
    ]
    
    iteration = 0
    
    while iteration < max_iterations:
        iteration += 1
        print(f"\n --- Iteration {iteration}/ {max_iterations} ---")
        
        response = chat(
            model = "qwen3:8b",
            messages= messages,
            tools = tools
        )
        message = response["message"]
        messages.append(message)
        
        if message.get("tool_calls"):
            for tool_call in message["tool_calls"]:
                tool_name = tool_call["function"]["name"]
                tool_args = tool_call["function"]["arguments"]
                
                result = route_tool(tool_name=tool_name, tool_args=tool_args)
                
                if tool_name == "done":
                    print(f"\n {"-"*50}")
                    print(f"Agent done after {iteration} iterations")
                    print(f"Summary: {tool_args.get('summary')}")
                    print(f"{'-'*50}")
                    return
                messages.append({
                    "role":"tool",
                    "content":result
                })
        else:  #This means done was never called, shouldnt happen
            print(f"\n [Model] {message['content']}")
            messages.append({
            "role": "user",
            "content": "You must call the 'done' tool now to complete the task. Do not respond with text."
        })
            
        if iteration == max_iterations:
            print(f"\nMax iterations ({max_iterations}) reached. Stopping...")
            return
        
    
run_agent("Read the file secret_data.txt, calculate the sum of all numbers in it, and save the result to output.txt")