# llm_client.py: el módulo que habla con el modelo de lenguaje (Etapa 2 del Proyecto Integrador).
# Mismo patrón que weather.py: no pide datos ni imprime; recibe un texto, consulta y devuelve texto.
# Si algo sale mal, lanza un error claro para que assistant.py lo maneje.
import os

import requests
from dotenv import load_dotenv

load_dotenv()

URL = "https://api.groq.com/openai/v1/chat/completions"
DEFAULT_MODEL = "openai/gpt-oss-20b"


# Un error propio: una clase que hereda de EnvironmentError (un error de Python ya existente).
# Nos permite atrapar específicamente "falta la clave" y dar un mensaje claro.
# El cuerpo es solo el docstring: no necesita nada más.
class MissingAPIKeyError(EnvironmentError):
    """Se lanza cuando falta la variable de entorno GROQ_API_KEY."""


# system_prompt tiene un valor por defecto: si quien llama no lo pasa, se usa ese.
# Así la función sirve para cualquier asistente, no solo para Rodados Sur.
def call_language_model(prompt, system_prompt="Eres un asistente útil. Responde en español."):
    """Envía el prompt a un modelo de lenguaje de Groq y devuelve la respuesta como texto."""
    api_key = os.getenv("GROQ_API_KEY")
    # Validamos antes de llamar: mejor un mensaje claro que un 401 misterioso.
    if not api_key:
        raise MissingAPIKeyError("falta GROQ_API_KEY en el archivo .env.")

    headers = {
        "Authorization": f"Bearer {api_key}",
        "Content-Type": "application/json",
    }
    payload = {
        "model": os.getenv("GROQ_MODEL", DEFAULT_MODEL),
        # La conversación ahora se arma con lo que recibe la función.
        "messages": [
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": prompt},
        ],
        "temperature": 0.3,
        "max_tokens": 500,
        "reasoning_effort": "low",
        "include_reasoning": False,
    }
    # Errores de red o HTTP (sin internet, timeout, 401 clave mala, 429 demasiadas requests...).
    try:
        response = requests.post(URL, headers=headers, json=payload, timeout=30)
        response.raise_for_status()
    except requests.exceptions.RequestException as exc:
        raise ConnectionError(f"no pude hablar con el modelo ({exc}).") from exc

    # Errores de formato: la respuesta no es JSON (ValueError) o no trae las claves esperadas
    # (KeyError) o la lista choices viene vacía (IndexError). Se atrapan varios con una tupla.
    try:
        data = response.json()
        text = data["choices"][0]["message"]["content"]
    except (ValueError, KeyError, IndexError) as exc:
        raise ValueError("el modelo devolvió una respuesta con un formato inesperado.") from exc
    # Una respuesta vacía tampoco sirve.
    if not text:
        raise ValueError("el modelo devolvió una respuesta vacía.")
    # .strip() quita espacios y saltos de línea sobrantes al principio y al final.
    return text.strip()


# Prueba del módulo: solo corre con "python llm_client.py".
if __name__ == "__main__":
    print(call_language_model("Explica en una oración qué es un modelo de lenguaje."))
