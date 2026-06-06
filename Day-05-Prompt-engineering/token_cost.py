from google import genai
import os
from dotenv import load_dotenv

load_dotenv()
client = genai.Client(api_key=os.getenv("Gemini_API_Key"))

# fewshot

prompt = """
    Extract the information from the text, respond only in JSON format
    
    Text: I am Asim Poudel currently living in Bhaktapur. I am 20 years old and I am a student.
    Output:{
        "name" = "Asim",
        "age" = "20",
        "city" = "Bhaktapur",
        "job" = "Jobless"
    }
    Text: I am Michael Jackson, currently living in California. I am 47 years old and I perform in dance shows.
    Output:
"""
response = client.models.generate_content(
    model = "gemini-2.5-flash",
    contents = prompt
)
print(response.text)

with open(r"Day-05-Prompt-engineering\token_cost.text","a") as file:
    file.write(f"\nFewshot (3): {response.usage_metadata}\n\n\n\n")

#     Text: I am Ram currently living in Ayodhya. I am 33 years old and I fight for my country.
#     Output:{
#         "name" = "Ram",
#         "age" = "33",
#         "city" = "Ayodhya",
#         "job" = "Soilder"
#     }
#     Text: I am Ganesh Shrestha currently living in Kathmandu. I am 33 years old and I act in movies.
#     Output:{
#         "name" = "Ganesh",
#         "age" = "33",
#         "city" = "Kathmandu",
#         "job" = "Actor"
#     }
    # Text: I am Riya Sharma currently living in Newyork. I am 27 years old and I teach in colleges.
    # Output:{
    #     "name" = "Riya",
    #     "age" = "27",
    #     "city" = "Newyork",
    #     "job" = "Teacher"
    # }
    
    # Text: I am Hari Kunwar currently living in Lalitpur. I am 30 years old and I am a student.
    # Output:{
    #     "name" = "Hari",
    #     "age" = "30",
    #     "city" = "Lalitpur",
    #     "job" = "Jobless"
    # }