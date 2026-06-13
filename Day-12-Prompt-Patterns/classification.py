from google import genai
from google.genai import types
from dotenv import load_dotenv
import os
import json
load_dotenv()
from pydantic import BaseModel

class SentimentResponse(BaseModel):
    label: str
    confidence: float
    
def classify(text):
    client = genai.Client(api_key=os.getenv("Gemini_API_Key"))
    instruction = """
    You are a amazing sentiment analyzer.
    Classify the text based on sentiment in three labels: Positive, Negative and Neutral. 
    Include confidence score, on how confident you are about the sentiment.
    Use JSON format only
    {
        "label":"Positive",
        "confidence":0.98
    }
    """
    response = client.models.generate_content(
        model = "gemini-2.5-flash-lite",
        contents = text,
        config=types.GenerateContentConfig(
            system_instruction= instruction
        )
    )
    data = response.text
    data = data.replace("```json","")
    data = data.replace("```","")
    
    try:
        parsed = json.loads(data)
        result = SentimentResponse(**parsed)
        print(result.label)
        print(result.confidence)
        if result.confidence >= 0.8:
            print("High confidence")
        elif result.confidence >= 0.4:
            print("Moderate confidence")
        else:
            print("Low confidence")
        return result

    except Exception as e:
        print(f"Error: {e}")
        return SentimentResponse(
            label="ERROR",
            confidence=0.0
        )
    
# sentiment = input("Enter sentiment:")
# classify(sentiment)