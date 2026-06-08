from google import genai
from dotenv import load_dotenv
import os
import time
from google.genai import types
load_dotenv()

client = genai.Client(api_key=os.getenv("Gemini_API_Key"))
email = """Dear Customer,
We are excited to announce our Summer Learning Sale. For the next 7 days, all premium courses on our platform are available at 40% off. This includes courses on AI Engineering, Data Science, Web Development, and Cloud Computing.
The discount will be automatically applied at checkout. Don't miss this opportunity to upgrade your skills at a reduced price.
Offer ends on June 15.

Best regards,
Learning Hub Team"""
fewshot_prompt = """Generate appropriate subject of email based on the body.

Email:
We are excited to announce the launch of our new AI Engineering course starting next month. Enroll now to secure your seat.

Subject:
Introducing Our New AI Engineering Course

Email:
Your order #45872 has been shipped and is expected to arrive within 3 business days. Track your package using the link provided.

Subject:
Your Order Is On Its Way

Email:
Join us this Friday for a free webinar on Prompt Engineering. Learn practical techniques and ask questions during the live session.

Subject:
Register for Our Free Prompt Engineering Webinar
"""
technique =["basic", "role","few-shot","xml","json"]
i=0
prompts = [
    f"""Generate appropriate subject of email based on the body.
    {email}""",
    f"""You are a professional email writer.
    Generate appropriate subject of email based on the body.
    {email}""",
    f"""{fewshot_prompt}\nEmail:{email}""",
    f"""
    <instruction>
    Generate appropriate subject of email based on the body.
    </instruction>
    
    <user_input>
    {email}
    </user_input>
    """,
    f"""Generate appropriate subject of email based on the body strictly in json format. Do not use any other format except json.
    {email}"""
    
]
for prompt in prompts:
    start = time.time()
    response = client.models.generate_content(
        model= "gemini-2.5-flash-lite",
        contents = f"{prompt}",
        config = types.GenerateContentConfig(
            system_instruction= "Generate response in a single line"
        )
    )
    end = time.time()
    data = response.text
    usage = response.usage_metadata
    candidate_token_count = usage.candidates_token_count
    total_token_count = usage.total_token_count
    prompt_token_count = usage.prompt_token_count
    response_time = end - start
    with open(r"Day-08-Project1\observation.txt","a",encoding="utf-8")as file:
        file.write(f"Technique: {technique[i]} \nPrompt: {prompt}\n\nResponse:\n{data}\n\ncandidate_token_count={candidate_token_count}\nprompt_token_count : {prompt_token_count}\ntotal_token_count = {total_token_count}\nresponse_time = {response_time:.2f}s\n\n")
    i+=1
        