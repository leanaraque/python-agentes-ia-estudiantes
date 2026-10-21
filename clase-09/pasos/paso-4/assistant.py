import os

from dotenv import load_dotenv

from llm_client import MissingAPIKeyError, chat_completion
from speech_input import listen_and_transcribe
from speech_output import speak
from tools import TOOLS, execute_tool

load_dotenv()

ASSISTANT_NAME = os.getenv("ASSISTANT_NAME", "Asistente")
MAX_STEPS = 5

FAQ = {
    "horario": "Abrimos de lunes a viernes de 9 a 13 y de 16 a 20, y los sábados de 9 a 13.",
    "dirección": "Estamos en Av. del Sur 1234.",
    "service": "El service básico cuesta $25.000 y el completo $45.000.",
    "demora": "El taller entrega las bicicletas en 48 horas hábiles.",
    "alquiler": "Alquilamos bicicletas urbanas a $8.000 por día.",
}


def build_system_prompt():
    """Arma las instrucciones del agente: rol, información del negocio y cuándo usar cada herramienta."""
    business_info = ""
    for answer in FAQ.values():
        business_info += f"- {answer}\n"
    return f"""Eres {ASSISTANT_NAME}, el asistente virtual de Rodados Sur, una tienda y taller de bicicletas de barrio.

Tu tarea es responder las consultas de los clientes. Recuerdas lo que el cliente dijo antes en esta conversación.

### Información del negocio
{business_info}
### Herramientas
- Si preguntan por una orden de reparación, usa get_order_status con el número de orden. Si no te dieron el número, pídelo.
- Si preguntan por el clima o si conviene salir en bici, usa get_weather.
- Si la respuesta no está en la información del negocio ni en las herramientas, o el caso es urgente, la consulta es para Marta. Primero pide el nombre y un teléfono o email para que Marta lo contacte, sin usar todavía hand_off_to_marta. Cuando el cliente te los dé (o diga que no quiere darlos), usa hand_off_to_marta una sola vez y avísale que Marta se va a comunicar.
- Si el cliente solo saluda, salúdalo y pregúntale en qué lo puedes ayudar: no le pidas datos.

### Reglas
- No inventes precios, horarios, productos, fechas ni datos.
- Responde en español, con tono cordial, en un máximo de 3 oraciones.
- Escribe en texto plano, sin asteriscos, listas ni emojis: tu respuesta también se escucha en voz alta.
- Escribe los precios con la palabra pesos, por ejemplo: 45.000 pesos."""


def choose_mode():
    """Pregunta cómo quiere conversar el cliente: por texto o por voz."""
    mode = input("¿Cómo quieres conversar? (texto/voz): ").strip().lower()
    if mode == "voz":
        print("Modo voz: presiona Enter y habla. También puedes escribir.")
        return "voz"
    print("Modo texto.")
    return "texto"


def get_user_input(mode):
    """Pide un mensaje: por teclado o, en modo voz, por el micrófono."""
    if mode == "texto":
        return input("Tú: ")
    typed = input("Tú (Enter para hablar): ")
    if typed.strip():
        return typed
    text = listen_and_transcribe()
    print(f"Tú (voz): {text}")
    return text


def run_agent(messages):
    """Bucle del agente: el modelo responde o pide herramientas, hasta llegar a una respuesta."""
    for step in range(MAX_STEPS):
        message = chat_completion(messages, tools=TOOLS)
        messages.append(message)
        tool_calls = message.get("tool_calls")
        if not tool_calls:
            return message.get("content") or "No tengo una respuesta. Se lo paso a Marta."
        for call in tool_calls:
            name = call["function"]["name"]
            arguments = call["function"]["arguments"]
            print(f"   [herramienta] {name} {arguments}")
            result = execute_tool(name, arguments)
            messages.append({"role": "tool", "tool_call_id": call["id"], "content": result})
    raise ValueError("el agente no llegó a una respuesta después de varios pasos.")


def main():
    print(f"Hola, soy {ASSISTANT_NAME}, el asistente de Rodados Sur.")
    print("Escribe 'salir' para terminar.")
    mode = choose_mode()
    messages = [{"role": "system", "content": build_system_prompt()}]
    history = []
    while True:
        try:
            message = get_user_input(mode)
        except (RuntimeError, ValueError, ConnectionError, MissingAPIKeyError) as error:
            print(f"{ASSISTANT_NAME}: Error controlado: {error}")
            continue
        if message.strip().lower().rstrip(".!") == "salir":
            break
        if not message.strip():
            print(f"{ASSISTANT_NAME}: Error controlado: el mensaje no puede estar vacío.")
            continue
        start = len(messages)
        messages.append({"role": "user", "content": message})
        try:
            answer = run_agent(messages)
        except (ValueError, ConnectionError, MissingAPIKeyError) as error:
            del messages[start:]
            print(f"{ASSISTANT_NAME}: Error controlado: {error}")
            continue
        history.append(message)
        print(f"{ASSISTANT_NAME}: {answer}")
        if mode == "voz":
            speak(answer)
    print(f"{ASSISTANT_NAME}: ¡Hasta luego! Consultas respondidas hoy: {len(history)}.")


if __name__ == "__main__":
    main()
