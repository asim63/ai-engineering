from google import genai
import os
from dotenv import load_dotenv

load_dotenv()

client = genai.Client(api_key=os.getenv("Gemini_API_Key"))

prompts = [
    "The ice-cream tasted really bad.",
    "The ice-cream was kinda alright half good half bad, i might try it next time or maybe not.",
    "The ice-cream was really really sweet. I wish i can eat it soon again.",
    "The ice-cream tasted amazing, but it melted too quickly."
]

for prompt in prompts:
    response = client.models.generate_content(
        model = "gemini-2.5-flash-lite",
        contents = f"""
            Classify the sentiment of this feedback as: positive negative or neutral.
            Feedback: {prompt}
            Answer only with the label.
        """
    )
    print(f"Prompt:v{prompt}\n Response: {response.text}\n")