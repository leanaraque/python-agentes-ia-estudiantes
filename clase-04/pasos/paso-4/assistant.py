import os

from dotenv import load_dotenv

from llm_client import MissingAPIKeyError, call_language_model_json
from weather import get_weather_report

load_dotenv()

ASSISTANT_NAME = os.getenv("ASSISTANT_NAME", "Asistente")

FAQ = {
    "horario": "Abrimos de lunes a viernes de 9 a 13 y de 16 a 20, y los sábados de 9 a 13.",
    "dirección": "Estamos en Av. del Sur 1234.",
    "service": "El service básico cuesta $25.000 y el completo $45.000.",
    "demora": "El taller entrega las bicicletas en 48 horas hábiles.",
    "alquiler": "Alquilamos bicicletas urbanas a $8.000 por día.",
}

INTENTS = ("horario", "direccion", "precios", "taller", "alquiler", "clima", "otro")
LEVELS = ("alta", "media", "baja")


def build_system_prompt():
    """Arma las instrucciones para el modelo con la información del FAQ y el formato JSON."""
    business_info = ""
    for answer in FAQ.values():
        business_info += f"- {answer}\n"
    return f"""Eres {ASSISTANT_NAME}, el asistente virtual de Rodados Sur, una tienda y taller de bicicletas de barrio.

Tu tarea es analizar la consulta del cliente y responderla.

### Información del negocio
{business_info}
### Reglas
- Usa solo la información del negocio. Si la respuesta no está ahí, escribe exactamente DESCONOCIDO en "respuesta" y "baja" en "confianza".
- No inventes precios, horarios, productos ni datos.
- Si preguntan por el clima o si conviene salir a andar en bici, la intención es "clima".
- La urgencia es "alta" si el cliente necesita la bicicleta pronto para trabajar o moverse.

### Formato de salida
Responde ÚNICAMENTE con un objeto JSON válido, sin texto antes ni después:
{{"intencion": "horario | direccion | precios | taller | alquiler | clima | otro", "urgencia": "alta | media | baja", "confianza": "alta | media | baja", "respuesta": "texto en español, cordial, máximo 2 oraciones"}}

### Ejemplo
Consulta: ¿Cuánto sale el service básico?
{{"intencion": "precios", "urgencia": "baja", "confianza": "alta", "respuesta": "El service básico cuesta $25.000."}}"""


def validate_analysis(data):
    """Comprueba que el análisis tenga todas las claves y valores permitidos."""
    if not isinstance(data, dict):
        raise ValueError("el análisis no es un objeto JSON.")
    for key in ("intencion", "urgencia", "confianza", "respuesta"):
        if key not in data:
            raise ValueError(f"al análisis le falta la clave '{key}'.")
    if data["intencion"] not in INTENTS:
        raise ValueError(f"intención desconocida: {data['intencion']}.")
    if data["urgencia"] not in LEVELS or data["confianza"] not in LEVELS:
        raise ValueError("urgencia o confianza con un valor no permitido.")
    return data


def get_user_input():
    """Pide un mensaje por consola y lo devuelve."""
    return input("Tú: ")


def call_ai_model(prompt):
    """Analiza la consulta con el modelo y decide qué responder."""
    if not prompt.strip():
        raise ValueError("el mensaje no puede estar vacío.")
    analysis = validate_analysis(call_language_model_json(prompt, build_system_prompt()))
    if analysis["intencion"] == "clima":
        return get_weather_report()
    if analysis["respuesta"] == "DESCONOCIDO" or analysis["confianza"] == "baja":
        return "No tengo ese dato. Se lo paso a Marta para que te responda."
    if analysis["urgencia"] == "alta":
        return analysis["respuesta"] + " Como es urgente, Marta te va a contactar hoy."
    return analysis["respuesta"]


def main():
    print(f"Hola, soy {ASSISTANT_NAME}, el asistente de Rodados Sur.")
    print("Escribe 'salir' para terminar.")
    history = []
    while True:
        message = get_user_input()
        if message.strip().lower() == "salir":
            break
        try:
            answer = call_ai_model(message)
        except (ValueError, ConnectionError, MissingAPIKeyError) as error:
            print(f"{ASSISTANT_NAME}: Error controlado: {error}")
            continue
        history.append(message)
        print(f"{ASSISTANT_NAME}: {answer}")
    print(f"{ASSISTANT_NAME}: ¡Hasta luego! Consultas respondidas hoy: {len(history)}.")


if __name__ == "__main__":
    main()
