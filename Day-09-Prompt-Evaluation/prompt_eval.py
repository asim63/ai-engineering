from google import genai
from google.genai import types
import os
from dotenv import load_dotenv
load_dotenv()
client = genai.Client(api_key=os.getenv("Gemini_API_Key"))
count = 0
test_set = [
    ("The food was amazing but the service was terrible.","Neutral"),

("I expected much worse actually.","Positive"),

("It wasn't bad.","Positive"),

("I don't know how I feel about it.","Neutral"),

("Thanks for ruining my day.","Negative"),

("The product works, but not as advertised.","Neutral"),
    # ("Haha, you made my day, thank you","Positive"),
    # ("Its so disgusting","Negative"),
    # ("Such a beautiful song","Positive"),
    # ("I didnt like it at first but now i somewhat understand the hype","Neutral"),
    # ("Get out of this place","Negative"),
    # ("The day is wonderful but i am so bored","Neutral"),
    # ("Nothing special.", "Neutral"),
    # ("I highly recommend it.", "Positive"),
    # ("Completely disappointed.", "Negative"),
    # ("It was acceptable.", "Neutral")
]
system_instruct = "Answer in one word : Positive, Negative or Neutral"
instruction = """
Classify the sentiment as Positive, Negative, or Neutral.

Review: I absolutely loved this movie.
Sentiment: Positive

Review: This was a complete waste of money.
Sentiment: Negative

Review: The product was okay, nothing special.
Sentiment: Neutral

"""
for statement,expected in test_set:
    prompt= f"""
    {instruction}
    Review: {statement}\nExpected:
    """
    response = client.models.generate_content(
        model = "gemini-3.1-flash-lite",
        contents = prompt,
        config = types.GenerateContentConfig(
            system_instruction = system_instruct
        )    
    )
    result = response.text.strip()
    if result == expected:
        count +=1
    with open(r"Day-09-Prompt-Evaluation\observation.txt","a") as file:
        file.write(
    f"Statement: {statement}\n"
    f"Expected: {expected}\n"
    f"Predicted: {result}\n\n"
    )  
accuracy = (count/len(test_set)) * 100    
with open(r"Day-09-Prompt-Evaluation\result.txt","a") as file:
    file.write(f"Few-shot: {accuracy}%\n")
