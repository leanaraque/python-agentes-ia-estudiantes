# llm_client.py, versión final de la Clase 4: respuestas en JSON y elección del proveedor
# (Groq en la nube u Ollama en la computadora) con la variable LLM_PROVIDER del .env.
# Mismo patrón que weather.py: no pide datos ni imprime; recibe un texto, consulta y devuelve texto.
# Si algo sale mal, lanza un error claro para que assistant.py lo maneje.
# json viene con Python: lo usamos para convertir la respuesta del modelo en dict.
import json
import os

import requests
from dotenv import load_dotenv

load_dotenv()

# Dos direcciones, mismo formato de request: el "enchufe" es igual, cambia a dónde se conecta.
GROQ_URL = "https://api.groq.com/openai/v1/chat/completions"
# localhost = esta misma computadora. 11434 es el puerto donde escucha Ollama.
OLLAMA_URL = "http://localhost:11434/v1/chat/completions"


# Un error propio: una clase que hereda de EnvironmentError (un error de Python ya existente).
# Nos permite atrapar específicamente "falta la clave" y dar un mensaje claro.
# El cuerpo es solo el docstring: no necesita nada más.
class MissingAPIKeyError(EnvironmentError):
    """Se lanza cuando falta la variable de entorno GROQ_API_KEY."""


# system_prompt tiene un valor por defecto: si quien llama no lo pasa, se usa ese.
# Así la función sirve para cualquier asistente, no solo para Rodados Sur.
# Nuevo parámetro temperature con valor por defecto 0.3: quien no lo pase, usa 0.3.
def call_language_model(prompt, system_prompt="Eres un asistente útil. Responde en español.", temperature=0.3):
    """Envía el prompt al modelo elegido en LLM_PROVIDER (groq u ollama) y devuelve el texto."""
    # El proveedor se elige en el .env; si no está, se usa Groq.
    provider = os.getenv("LLM_PROVIDER", "groq")
    if provider == "ollama":
        url = OLLAMA_URL
        # Ollama local no necesita clave, pero el formato de la request lleva una: cualquier texto sirve.
        api_key = "ollama"
        model = os.getenv("OLLAMA_MODEL", "qwen2.5:1.5b")
    else:
        url = GROQ_URL
        api_key = os.getenv("GROQ_API_KEY")
        # Solo Groq necesita clave: la validamos antes de llamar.
        if not api_key:
            raise MissingAPIKeyError("falta GROQ_API_KEY en el archivo .env.")
        model = os.getenv("GROQ_MODEL", "openai/gpt-oss-20b")

    headers = {
        "Authorization": f"Bearer {api_key}",
        "Content-Type": "application/json",
    }
    payload = {
        # El modelo depende del proveedor elegido arriba.
        "model": model,
        # La conversación ahora se arma con lo que recibe la función.
        "messages": [
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": prompt},
        ],
        # Ahora la temperatura viene del parámetro (para JSON usamos 0.1: queremos precisión).
        "temperature": temperature,
        "max_tokens": 500,
    }
    # Estos dos parámetros son propios del modelo de razonamiento de Groq: solo se agregan para Groq.
    # payload["clave"] = valor agrega una clave nueva a un dict que ya existe.
    if provider == "groq":
        payload["reasoning_effort"] = "low"
        payload["include_reasoning"] = False
    # Errores de red o HTTP (sin internet, timeout, 401 clave mala, 429 demasiadas requests...).
    try:
        # timeout de 60 segundos: un modelo local tarda más, sobre todo la primera vez que se carga.
        response = requests.post(url, headers=headers, json=payload, timeout=60)
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


# Extrae el JSON aunque el modelo lo envuelva con texto o con ```json ... ```.
def parse_json(text):
    """Extrae el objeto JSON de un texto (aunque traiga texto alrededor) y lo devuelve como dict."""
    # find busca la PRIMERA aparición de "{"; rfind busca la ÚLTIMA de "}". Si no encuentra, devuelve -1.
    start = text.find("{")
    end = text.rfind("}")
    if start == -1 or end == -1:
        raise ValueError("la respuesta no contiene un objeto JSON.")
    # text[start:end + 1] recorta el texto desde la primera llave hasta la última (incluida).
    # json.loads lanza JSONDecodeError si el JSON está mal escrito: es un tipo de ValueError.
    return json.loads(text[start:end + 1])


def call_language_model_json(prompt, system_prompt):
    """Pide al modelo una respuesta en JSON y la devuelve como dict. Si llega mal, pide que la corrija una vez."""
    # Temperatura baja: para datos estructurados queremos respuestas estables, no creativas.
    text = call_language_model(prompt, system_prompt, temperature=0.1)
    try:
        return parse_json(text)
    except ValueError:
        # Validación sintáctica + corrección: le devolvemos su propio texto y le pedimos el JSON correcto.
        fix_prompt = f"Este texto debía ser un JSON válido y no lo es. Devuelve solo el JSON corregido:\n{text}"
        fixed = call_language_model(fix_prompt, system_prompt, temperature=0.1)
        try:
            return parse_json(fixed)
        except ValueError as exc:
            # Si falla dos veces, nos rendimos con un error claro (lo atrapa assistant.py).
            raise ValueError("el modelo no devolvió un JSON válido.") from exc


# Prueba del módulo: pide un JSON con dos claves y muestra el dict que devuelve.
if __name__ == "__main__":
    # Los paréntesis permiten partir una llamada larga en varias líneas.
    # Las comillas simples ' ' dejan escribir comillas dobles " " adentro sin problemas.
    print(call_language_model_json(
        "¿Cuánto sale un service completo?",
        'Responde solo con JSON con este formato: {"tema": "...", "respuesta_corta": "..."}',
    ))
