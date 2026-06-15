import requests 
#GET
base_url = "https://randomuser.me/api/"
try:
    response = requests.get(base_url)
    data = response.json()
    print((data["results"][0]["name"]["first"]))
    print((data["results"][0]["gender"]))
except requests.exceptions.Timeout:
    print("Request Timed Out")

#Post
data = {
    "title": "Hello",
    "body": "Testing",
    "userId": 1
}

response = requests.post(
    "https://jsonplaceholder.typicode.com/posts",
    json=data,
    timeout=5
)

print(response.status_code)
print(response.json())