import os

import requests
from dotenv import load_dotenv

load_dotenv()

URL = "https://api.groq.com/openai/v1/chat/completions"

SYSTEM_PROMPT = """Eres Rayo, el asistente virtual de Rodados Sur, una tienda y taller de bicicletas de barrio.

Tu tarea es responder las consultas de los clientes sobre el negocio.

### Información del negocio
- Abrimos de lunes a viernes de 9 a 13 y de 16 a 20, y los sábados de 9 a 13.
- Estamos en Av. del Sur 1234.
- El service básico cuesta $25.000 y el completo $45.000.
- El taller entrega las bicicletas en 48 horas hábiles.
- Alquilamos bicicletas urbanas a $8.000 por día.

### Reglas
- Responde solo con la información del negocio. Si no la tienes, di que se lo pasas a Marta, la dueña.
- No inventes precios, horarios ni datos.
- Responde en español, con tono cordial, en un máximo de 3 oraciones."""

headers = {
    "Authorization": f"Bearer {os.getenv('GROQ_API_KEY')}",
    "Content-Type": "application/json",
}

payload = {
    "model": os.getenv("GROQ_MODEL", "openai/gpt-oss-20b"),
    "messages": [
        {"role": "system", "content": SYSTEM_PROMPT},
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
