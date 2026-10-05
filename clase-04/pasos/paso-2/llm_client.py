import json
import os

import requests
from dotenv import load_dotenv

load_dotenv()

URL = "https://api.groq.com/openai/v1/chat/completions"
DEFAULT_MODEL = "openai/gpt-oss-20b"


class MissingAPIKeyError(EnvironmentError):
    """Se lanza cuando falta la variable de entorno GROQ_API_KEY."""


def call_language_model(prompt, system_prompt="Eres un asistente útil. Responde en español.", temperature=0.3):
    """Envía el prompt a un modelo de lenguaje de Groq y devuelve la respuesta como texto."""
    api_key = os.getenv("GROQ_API_KEY")
    if not api_key:
        raise MissingAPIKeyError("falta GROQ_API_KEY en el archivo .env.")

    headers = {
        "Authorization": f"Bearer {api_key}",
        "Content-Type": "application/json",
    }
    payload = {
        "model": os.getenv("GROQ_MODEL", DEFAULT_MODEL),
        "messages": [
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": prompt},
        ],
        "temperature": temperature,
        "max_tokens": 500,
        "reasoning_effort": "low",
        "include_reasoning": False,
    }
    try:
        response = requests.post(URL, headers=headers, json=payload, timeout=30)
        response.raise_for_status()
    except requests.exceptions.RequestException as exc:
        raise ConnectionError(f"no pude hablar con el modelo ({exc}).") from exc

    try:
        data = response.json()
        text = data["choices"][0]["message"]["content"]
    except (ValueError, KeyError, IndexError) as exc:
        raise ValueError("el modelo devolvió una respuesta con un formato inesperado.") from exc
    if not text:
        raise ValueError("el modelo devolvió una respuesta vacía.")
    return text.strip()


def parse_json(text):
    """Extrae el objeto JSON de un texto (aunque traiga texto alrededor) y lo devuelve como dict."""
    start = text.find("{")
    end = text.rfind("}")
    if start == -1 or end == -1:
        raise ValueError("la respuesta no contiene un objeto JSON.")
    return json.loads(text[start:end + 1])


def call_language_model_json(prompt, system_prompt):
    """Pide al modelo una respuesta en JSON y la devuelve como dict. Si llega mal, pide que la corrija una vez."""
    text = call_language_model(prompt, system_prompt, temperature=0.1)
    try:
        return parse_json(text)
    except ValueError:
        fix_prompt = f"Este texto debía ser un JSON válido y no lo es. Devuelve solo el JSON corregido:\n{text}"
        fixed = call_language_model(fix_prompt, system_prompt, temperature=0.1)
        try:
            return parse_json(fixed)
        except ValueError as exc:
            raise ValueError("el modelo no devolvió un JSON válido.") from exc


if __name__ == "__main__":
    print(call_language_model_json(
        "¿Cuánto sale un service completo?",
        'Responde solo con JSON con este formato: {"tema": "...", "respuesta_corta": "..."}',
    ))
