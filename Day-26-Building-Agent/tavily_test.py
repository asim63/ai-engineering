from tavily import TavilyClient
import os
from dotenv import load_dotenv
load_dotenv()

client = TavilyClient(api_key=os.getenv("Tavily_API_Key"))
response = client.search(query="Who is leo messi?", max_results=3)
output = ""
for r in response["results"]:
    output += f"Title: {r['title']}\n"
    output += f"URL: {r['url']}\n"
    output += f"Content: {r['content']}\n"
    output += "-"*50 +"\n"
    
    print(output)