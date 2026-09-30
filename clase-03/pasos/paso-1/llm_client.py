import os

import requests
from dotenv import load_dotenv

load_dotenv()

URL = "https://api.groq.com/openai/v1/chat/completions"

headers = {
    "Authorization": f"Bearer {os.getenv('GROQ_API_KEY')}",
    "Content-Type": "application/json",
}

payload = {
    "model": os.getenv("GROQ_MODEL", "openai/gpt-oss-20b"),
    "messages": [
        {"role": "user", "content": "¿A qué hora abren el sábado?"},
    ],
    "temperature": 0.3,
    "max_tokens": 500,
    "reasoning_effort": "low",
    "include_reasoning": False,
}

response = requests.post(URL, headers=headers, json=payload, timeout=30)
print(response.status_code)

data = response.json()
print(data["choices"][0]["message"]["content"])
print(data["usage"])
