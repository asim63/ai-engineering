from pydantic import BaseModel, Field, ValidationError

import json
from ollama import chat

class MovieRecommendation(BaseModel):
    title: str
    year: int = Field(...,ge = 1888, le = 2030)
    genre: str
    reason: str

def get_movie_recommendation(mood: str) -> MovieRecommendation | None:
    prompt = f"""Recommend one movie for someone who feels '{mood}'.
    Respond with ONLY valid JSON, no extra text, no markdown fences, in this exact format:
    {{"title":"...", "year":"2020","genre":"...","reason":"..."}}"""
    
    response = chat(
        model="qwen3:8b",
        messages=[{"role":"user","content":prompt}],
        options={"temperature": 0}
    )
    raw = response["message"]["content"].strip()
    
    try:
        data = json.loads(raw)
        return MovieRecommendation(**data)
    except (json.JSONDecodeError, ValidationError) as e:
        print("validation Failed", e)
        return None
    
    
result = get_movie_recommendation("nostalgic and cozy")
print(result)