from google import genai
import os
from dotenv import load_dotenv

load_dotenv()
client = genai.Client(api_key=os.getenv("Gemini_API_Key"))

# zeroshot
# prompt = """
#     Extract the information from the text, respond only in JSON format
    
#     {
#         "name" = "",
#         "age" = "",
#         "city" = "",
#         "job" = ""
#     }
    
#     Text: I am Asim Poudel currently living in Bhaktapur. I am 20 years old and i am a student.
# """

# response = client.models.generate_content(
#     model = "gemini-2.5-flash-lite",
#     contents = prompt
# )
# print(response.text)

# fewshot

prompt = """
    Extract the information from the text, respond only in JSON format
    
    Text: I am Asim Poudel currently living in Bhaktapur. I am 20 years old and i am a student.
    Output:{
        "name" = "Asim",
        "age" = "20",
        "city" = "Bhaktapur",
        "job" = "Jobless"
    }
    
    
    Text: I am Riya Sharma currently living in Newyork. I am 27 years old and I am a teacher.
    Output:{
        "name" = "Riya",
        "age" = "27",
        "city" = "Newyork",
        "job" = "Teacher"
    }
    
    # Text: I am Michael Jackson, currently living in California. I am 47 years old and i am a student.
    Output:
"""
response = client.models.generate_content(
    model = "gemini-2.5-flash-lite",
    contents = prompt
)
print(response.text)