from ollama import chat
import math

#Making a tool
calculator_tool = {
    "type":"function",
    "function": {
        "name":"calculator",
        "description": "Performs arithmetic calculations. Use this or ANY math operation - addition, subtraction, multiplication, division, modulo, powers, square roots. Always use this instead of calculating yourself.",
        "parameters": {
            "type":"object",
            "properties":{
                "expression":{
                "type":"string",
                "description": "The math expression to evaluate. Examples: '23 + 47', '100/4','sqrt(49),'15/100 * 32'"
            }
        },
        "required": ["expression"]
      }
    }
}

#Python function

def calculator(expression: str) -> str:
    try:
        result = eval(
            expression,
            {__builtins__:{}}, # this is for security concern, disables all builtin python functions
            {"sqrt":math.sqrt, "pow":pow, "abs": abs, "round":round}

        )
        return str(result)
    
    except Exception as e:
        return f"Error: {e}"


def run_agent(user_message:str):
    messages = [{
        "role":"user",
        "content":user_message
    }]
    print(f"\nUser: {user_message}")

    while True:
        response = chat(
            model = "qwen3:8b",
            messages=messages,
            tools=[calculator_tool]
        )
        message = response["message"]
        messages.append(message)
        
        if message.get("tool_calls"):
            for tool_call in message["tool_calls"]:
                print(f"Tool call ID: {tool_call.get('id')}") 
                tool_name = tool_call["function"]["name"]
                tool_args = tool_call["function"]["arguments"]

                print(f"\nModel calls: {tool_name}")
                print(f"With: {tool_args}")
                
                if tool_name == "calculator":
                    result = calculator(tool_args["expression"])
                else:
                    result = "Tool not found"
                
                print(f"Result: {result}")

                messages.append({
                    "role":"tool",
                    "content": result
                })

        else:
            print(f"\n Final Answer: {message['content']}")
            break
        
run_agent("First tell me what 1234 * 5678 is, then separately tell me what 8765 * 4321 is")
