from guardrails import Guard
from pydantic import BaseModel,Field
from ollama import chat

class MovieRecommendation(BaseModel):
    title:str
    year:int = Field(..., ge= 1888, le = 2030)
    genre:str
    reason:str
    
    
guard = Guard.for_pydantic(output_class=MovieRecommendation)

def call_ollama(prompt:str)-> str:
    response = chat(
        model = "qwen3:8b",
        messages=[{"role":"user","content":prompt}],
        options={"temperature": 0.0}

    )
    return response["message"]["content"]

prompt = """Recommend one movie for someone who feels melancholic.
Response with ONLY valid JSON in this shape:
{"title":"...","year":"2020","genre": "...","reason":"..."}"""

raw_output = call_ollama(prompt=prompt)
validated = guard.parse(raw_output)
print(validated.validated_output)