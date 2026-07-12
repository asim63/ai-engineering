import json
import ollama
from pydantic import BaseModel, Field, ValidationError

class MovieRecommendation(BaseModel):
    title: str
    year: int = Field(..., ge=1888, le=2030)
    genre: str
    reason: str

def get_movie_with_retry(mood: str, max_retries: int = 3) -> MovieRecommendation | None:
    base_prompt = f"""Recommend one movie for someone who feels "{mood}".
Respond with ONLY valid JSON, no extra text, no markdown fences, in this exact shape:
{{"title": "...", "year": 2020, "genre": "...", "reason": "..."}}"""

    messages = [{"role": "user", "content": base_prompt}]

    for attempt in range(1, max_retries + 1):
        response = ollama.chat(model="qwen3:8b", messages=messages, options={"temperature": 0})
        raw = response["message"]["content"].strip()

        try:
            data = json.loads(raw)
            return MovieRecommendation(**data)
        except (json.JSONDecodeError, ValidationError) as e:
            print(f"Attempt {attempt} failed: {e}")
            # Feed the error back to the model and ask it to correct itself
            messages.append({"role": "assistant", "content": raw})
            messages.append({
                "role": "user",
                "content": f"That response was invalid. Error: {e}. "
                            f"Return ONLY corrected valid JSON matching the exact shape requested, nothing else."
            })

    print("All retries exhausted.")
    return None

result = get_movie_with_retry("adventurous and bold")
print(result)