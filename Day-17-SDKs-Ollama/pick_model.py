from google import genai
from google.genai import types
from dotenv import load_dotenv
import os
import json
load_dotenv()
from pydantic import BaseModel

class TaskResponse(BaseModel):
    task: str

client = genai.Client(api_key=os.getenv("Gemini_API_Key"))
def classify(prompt):
        response = client.models.generate_content(
            model = "gemini-2.5-flash",
            contents = prompt,
            config = types.GenerateContentConfig(
                system_instruction="""
                Classify the request as any one either:
                - classification
                - debugging
                - summarization
                - generation 
                - extraction
                - code_explanation
                {
                    "task": "classification"
                }

                Return ONLY valid JSON.
                - No markdown.
                - No explanation.
                -Only JSON.
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
    
def pick_model(task):
    if task == "classification":
        return "flash-lite"

    elif task == "extraction":
        return "flash-lite"

    elif task == "summarization":
        return "flash"

    elif task == "generation":
        return "flash"

    elif task == "code_explanation":
        return "flash"

    elif task == "debugging":
        return "flash"

    return "flash"


prompt = "Summarize this: I fell in the way back to the college, i had wound all over my legs and hands."
task = classify(prompt).task
print(task)
model_version = pick_model(task)
model = "gemini-2.5-"+ model_version
print("Gonna use this model: "+ model)
response = client.models.generate_content(
    model = model,
    contents = prompt
)
print(response.text)