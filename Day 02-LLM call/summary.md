# Day 02- LLM call

## API connection
- Learned to Create API Key from https://aistudio.google.com/
- Installed the google-genai package using pip command:
```bash
pip install -U google-genai
```
```python
from google import genai

client = genai.Clients()
```

## dotenv
- Created a .env file
- Learned to use python-dotenv package.
```bash
pip install python-dotenv
```

```python
import os
from dotenv import load_dotenv

load_dotenv()

api_key = os.getenv("API_KEY")
```

## Response Body

- Learned Gemini response objects and usage metadata.
- Learned how input and output tokens are tracked.
- Learned how token usage impact LLM performance and limits.
```python
print(response)
print(response.text)
print(response.usage_metadata)
```