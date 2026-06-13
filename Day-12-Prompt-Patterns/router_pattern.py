from google import genai
from google.genai import types
from dotenv import load_dotenv
import os
import json
from pydantic import BaseModel

from classification import classify
from extraction import extract
from generation import generate
from summarize import summarize

load_dotenv()

client = genai.Client(api_key=os.getenv("Gemini_API_Key"))

class ClassifyTask(BaseModel):
    task: str

def classify_task(text):
    response = client.models.generate_content(
        model="gemini-2.5-flash-lite",
        contents=text,
        config=types.GenerateContentConfig(
            system_instruction="""
Classify the request as any one either:
- summarize
- classify
- generate
- extract

{
    "task": "extract"
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
        result = ClassifyTask(**parsed)
        print(result)
        return result

    except Exception as e:
        print(f"Error: {e}")
        return ClassifyTask(task="UNKNOWN")

para = input("Enter the task you want to perform:\n")

task = classify_task(para).task

if task == "summarize":
    summarize(para, "bullet")

elif task == "extract":
    extract(para)

elif task == "classify":
    classify(para)

elif task == "generate":
    generate(para)

else:
    print("Unknown task")