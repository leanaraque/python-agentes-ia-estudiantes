# llm_client.py, versión de la Clase 5: la llamada al modelo ahora recibe la CONVERSACIÓN
# completa (una lista de mensajes) y puede ofrecerle herramientas al modelo.
import json
import os

import requests
from dotenv import load_dotenv

load_dotenv()

GROQ_URL = "https://api.groq.com/openai/v1/chat/completions"
OLLAMA_URL = "http://localhost:11434/v1/chat/completions"


class MissingAPIKeyError(EnvironmentError):
    """Se lanza cuando falta la variable de entorno GROQ_API_KEY."""


# Función nueva y central: recibe la lista de mensajes tal cual (system, user, assistant, tool...).
# tools=None: si no se pasan herramientas, la request es igual a la de siempre.
def chat_completion(messages, tools=None, temperature=0.3):
    """Envía la conversación completa al modelo y devuelve su mensaje (un dict)."""
    provider = os.getenv("LLM_PROVIDER", "groq")
    if provider == "ollama":
        url = OLLAMA_URL
        api_key = "ollama"
        model = os.getenv("OLLAMA_MODEL", "qwen2.5:1.5b")
    else:
        url = GROQ_URL
        api_key = os.getenv("GROQ_API_KEY")
        if not api_key:
            raise MissingAPIKeyError("falta GROQ_API_KEY en el archivo .env.")
        model = os.getenv("GROQ_MODEL", "openai/gpt-oss-20b")

    headers = {
        "Authorization": f"Bearer {api_key}",
        "Content-Type": "application/json",
    }
    payload = {
        "model": model,
        # Toda la conversación viaja en cada llamada: eso es la MEMORIA de corto plazo.
        "messages": messages,
        "temperature": temperature,
        "max_tokens": 500,
    }
    # Si hay herramientas, se agregan al cuerpo: el modelo ve su nombre, descripción y parámetros
    # y puede PEDIR usarlas en lugar de responder.
    if tools:
        payload["tools"] = tools
    if provider == "groq":
        payload["reasoning_effort"] = "low"
        payload["include_reasoning"] = False
    try:
        response = requests.post(url, headers=headers, json=payload, timeout=60)
        response.raise_for_status()
    except requests.exceptions.RequestException as exc:
        raise ConnectionError(f"no pude hablar con el modelo ({exc}).") from exc

    try:
        # Devolvemos el mensaje completo (un dict) y no solo el texto: si el modelo pide una
        # herramienta, el pedido viene en la clave "tool_calls" y no hay "content".
        return response.json()["choices"][0]["message"]
    except (ValueError, KeyError, IndexError) as exc:
        raise ValueError("el modelo devolvió una respuesta con un formato inesperado.") from exc


# La función de las clases anteriores sigue existiendo (y funcionando igual): ahora arma una
# conversación de dos mensajes y usa chat_completion por dentro.
def call_language_model(prompt, system_prompt="Eres un asistente útil. Responde en español.", temperature=0.3):
    """Envía un prompt (con sus instrucciones) al modelo y devuelve solo el texto de la respuesta."""
    messages = [
        {"role": "system", "content": system_prompt},
        {"role": "user", "content": prompt},
    ]
    # .get("content") devuelve None (en lugar de dar error) si la clave no existe.
    text = chat_completion(messages, temperature=temperature).get("content")
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
    # Muestra el dict completo que devuelve el modelo: role y content.
    print(chat_completion([{"role": "user", "content": "Saluda en una oración."}]))
