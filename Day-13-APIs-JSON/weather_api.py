from dotenv import load_dotenv
import requests
import os

load_dotenv()

url = "https://api.openweathermap.org/data/2.5/weather"
user_input = input("Enter city: ")

key = os.getenv("Weather_API_Key")

params = {
    "q": user_input,
    "units": "imperial",
    "appid": key
}

print("sending request...")
response = requests.get(url, params=params, timeout=10)

print("request received")

data = response.json()

# safety check
if response.status_code != 200:
    print("Error:", data)
    exit()

print(f"\n{user_input}:")

print("Weather:", data["weather"][0]["main"])
print("Description:", data["weather"][0]["description"])
print("Temperature:", data["main"]["temp"])
print("Country:", data["sys"]["country"])