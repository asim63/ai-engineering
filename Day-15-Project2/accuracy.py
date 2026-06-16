from google import genai
from google.genai import types
from dotenv import load_dotenv
import os
import json
from pydantic import BaseModel
load_dotenv()
client = genai.Client(api_key= os.getenv("Gemini_API_Key"))

class TaskResponse(BaseModel):
    task : str

def classify(prompt):
        response = client.models.generate_content(
            model = "gemini-2.0",
            contents = prompt,
            config = types.GenerateContentConfig(
                system_instruction="""
                Classify the request as any one either:
                - explain
                - debug
                - complexity
                - NoCode

                {
                    "task": "explain"
                }

                Return ONLY valid JSON.
                - No markdown.
                - No explanation.
                - Only JSON.
                """
                
            )
        )
        data = response.text
        data = data.replace("```json", "")
        data = data.replace("```", "")

        try:
            parsed = json.loads(data)
            result = TaskResponse(**parsed)
            print(f"Task: {result}")
            return result

        except Exception as e:
            print(f"Error: {e}")
            return TaskResponse(task="UNKNOWN")
        
test_set = [
    ("Explain this code: for i in range(5): print(i)", "explain"),
    ("What does this function do? def add(a,b): return a+b", "explain"),
    ("Can you explain recursion?", "explain"),
    ("Debug this code: for i in range(5) print(i)", "debug"),
    ("Why am I getting IndexError here?", "debug"),
    ("Fix the bug in this code", "debug"),
    ("What is the time complexity of binary search?", "complexity"),
    ("Find the space complexity of this algorithm", "complexity"),
    ("Complexity of quicksort?", "complexity"),
    ("Hello", "NoCode"),
    ("Who are you?", "NoCode"),
    ("Tell me a joke", "NoCode"),
    ("What is Python?", "NoCode"),
    ("Explain the complexity of this loop", "complexity"),
    ("Why does this code crash?", "debug")
]
count = 0
for review, result in test_set:
    task = classify(review).task
    
    if task == result:
        count = count + 1
        

accuracy = count/len(test_set) * 100
print(f"accuracy = {accuracy}%")