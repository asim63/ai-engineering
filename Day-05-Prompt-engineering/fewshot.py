from google import genai
import os
from dotenv import load_dotenv
load_dotenv()

client = genai.Client(api_key=os.getenv("Gemini_API_Key"))

prompt = """
Classify the review using ONLY one of these labels:

Positive
Negative
Neutral

If both positive and negative opinions are present,
classify according to the overall sentiment.

Review: The ice-cream was delicious.
Sentiment: Positive

Review: The ice-cream tasted awful.
Sentiment: Negative

Review: The ice-cream was yummy, but it was so less.
Sentiment: Neutral

Review: The ice-cream tasted amazing, but it melted pretty early.
Sentiment:
"""

response = client.models.generate_content(
    model = "gemini-2.5-flash-lite",
    contents = prompt
)
print(response.text)