from google import genai
from dotenv import load_dotenv
import os

load_dotenv()
client = genai.Client(api_key=os.getenv("Gemini_API_Key"))

history = []
prompts = ["Hi whats up?","I am Asim","Nice to meet you","Goodbye"]
summary = ""
MAX_HISTORY = 4
for prompt in prompts:
    history.append( {
        "role": "user",
        "parts":[{"text": f"{prompt}"}]
    })
    if (len(history)) > MAX_HISTORY:
        old_message = history[:-MAX_HISTORY]
        summary = client.models.generate_content(
            model = "gemini-3.1-flash-lite",
            contents =f"""
            Existing Summary:
            {summary}

            New Messages:
            {old_message}

            Update the summary.
            Preserve important information.
            """
        ).text
        history = history[-MAX_HISTORY:]
        
    response = client.models.generate_content(
        model = "gemini-2.5-flash-lite",
        contents = f"""Summary: {summary}, History:{history}"""
    )
    data = response.text
    usage = response.usage_metadata
    with open(r"Day-10-Context-Management\check_prompt_usage.txt","a", encoding = "utf-8") as file:
        file.write(
    f"""
    Prompt: {prompt}
    Input Tokens: {usage.prompt_token_count}
    Output Tokens: {usage.candidates_token_count}
    Total Tokens: {usage.total_token_count}
    """
)
    history.append({
        "role":"model",
        "parts":[{"text":f"{response.text}"}]
    })
   
    