#connect to an API using python
import requests

base_url = "https://catfact.ninja/fact"

def get_response():
    try:
        response = requests.get(base_url)

        if response.status_code == 200:
            print("Success!")
            return response.json()
        else:
            print(f"Failed {response.status_code}")
    except requests.exceptions.Timeout:
        print("Request timed out.")

cat_info = get_response()
print(cat_info["fact"])


# #Query Params
# url = "https://api.example.com/search?q=python"

# params = {
#     "q": "python"
# }

# response = requests.get(
#     url,
#     params=params
# )

#better approach
url = "https://api.example.com/search?q=python"
try:
    response = requests.get(url, timeout=10)

except requests.exceptions.Timeout:
    print("Request timed out")