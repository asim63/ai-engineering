from google import genai
from dotenv import load_dotenv
import os
from google.genai import types
load_dotenv()

client = genai.Client(api_key=os.getenv("Gemini_API_Key"))
email = """Dear Customer,
We are excited to announce our Summer Learning Sale. For the next 7 days, all premium courses on our platform are available at 40% off. This includes courses on AI Engineering, Data Science, Web Development, and Cloud Computing.
The discount will be automatically applied at checkout. Don't miss this opportunity to upgrade your skills at a reduced price.
Offer ends on June 15.

Best regards,
Learning Hub Team"""

observation = [
{   "Technique": "Basic",
    "Response": "☀️ 40% Off All Premium Courses - Summer Learning Sale Ends June 15!"
},    
{   "Technique": "Role", 
    "Response": "☀️ 7-Day Summer Learning Sale: 40% Off All Premium Courses!"
},
{   "Technique": "Few-shot", 
    "Response": "☀️ Summer Learning Sale: 40% Off All Premium Courses!"
},
{   "Technique": "XML" ,
    "Response": "☀️ 40% Off All Premium Courses - Summer Learning Sale!"
},
{   "Technique": "JSON", 
    "Response":"🔥 40% OFF Summer Learning Sale: AI, Data Science, Web Dev & More!"
}
]
for obv in observation:
     prompt = f"""
     You are quite perfectionist and dont like any flaw at all. You are a specialist in writing email. You judge the email with your vast knowledge and specially rate the subject of email.
     Email : {email}
     Subject: {obv["Response"]}
     
     Rate the subject of email out of 10. Only write a single number from 1 to 10 nothing else.
     """
     
     response = client.models.generate_content(
         model = "gemini-3.1-flash-lite",
        contents = prompt,
        config = types.GenerateContentConfig(
            system_instruction = "Rate from between 1-10, no text just number"
        ) 
     )
     with open(r"Day-09-Prompt-Evaluation\judgement.txt","a",encoding="utf-8") as file:
         file.write(f"---{obv["Technique"]}---\nSubject : {obv['Response']} \nScore : {response.text}/10 \n\n")