# assistant.py, versión de la Clase 5: Rayo es un AGENTE. Tiene memoria (la lista de mensajes)
# y herramientas (tools.py), y un bucle que decide cuándo usarlas.
import os

from dotenv import load_dotenv

# chat_completion recibe la conversación completa y las herramientas.
from llm_client import MissingAPIKeyError, chat_completion
from tools import TOOLS, execute_tool

# Carga el .env (nombre del asistente, clave de Groq, modelo, coordenadas).
load_dotenv()

ASSISTANT_NAME = os.getenv("ASSISTANT_NAME", "Asistente")
# Límite de vueltas del bucle: evita que el agente quede pidiendo herramientas para siempre.
MAX_STEPS = 5

# La información del negocio: el modelo la recibe como contexto en el prompt.
FAQ = {
    "horario": "Abrimos de lunes a viernes de 9 a 13 y de 16 a 20, y los sábados de 9 a 13.",
    "dirección": "Estamos en Av. del Sur 1234.",
    "service": "El service básico cuesta $25.000 y el completo $45.000.",
    "demora": "El taller entrega las bicicletas en 48 horas hábiles.",
    "alquiler": "Alquilamos bicicletas urbanas a $8.000 por día.",
}


# El rol del agente y CUÁNDO usar cada herramienta: el modelo decide leyendo esto y las fichas de TOOLS.
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
- Si la respuesta no está en la información del negocio ni en las herramientas, o el caso es urgente, usa hand_off_to_marta y avísale al cliente que Marta se va a comunicar.

### Reglas
- No inventes precios, horarios, productos, fechas ni datos.
- Responde en español, con tono cordial, en un máximo de 3 oraciones."""


# Entrada por consola (en la Clase 6 se suma la voz).
def get_user_input():
    """Pide un mensaje por consola y lo devuelve."""
    return input("Tú: ")


# El BUCLE DE CONTROL del agente: la pieza que faltaba (las otras ya las teníamos: LLM, rol,
# memoria y herramientas). Repite: preguntar al modelo, ejecutar lo que pide, devolverle el resultado.
def run_agent(messages):
    """Bucle del agente: el modelo responde o pide herramientas, hasta llegar a una respuesta."""
    # range(MAX_STEPS): como mucho 5 vueltas.
    for step in range(MAX_STEPS):
        message = chat_completion(messages, tools=TOOLS)
        # Todo lo que dice el modelo queda en la memoria, incluidos sus pedidos de herramientas.
        messages.append(message)
        tool_calls = message.get("tool_calls")
        # Si no pidió herramientas, ya respondió: salimos del bucle con el texto.
        if not tool_calls:
            return message.get("content") or "No tengo una respuesta. Se lo paso a Marta."
        # Puede pedir más de una herramienta a la vez: las ejecutamos todas.
        for call in tool_calls:
            name = call["function"]["name"]
            arguments = call["function"]["arguments"]
            # Mostramos qué herramienta usa: así "vemos pensar" al agente durante la clase.
            print(f"   [herramienta] {name} {arguments}")
            result = execute_tool(name, arguments)
            # El resultado vuelve con el rol "tool" y el id del pedido al que responde.
            messages.append({"role": "tool", "tool_call_id": call["id"], "content": result})
    raise ValueError("el agente no llegó a una respuesta después de varios pasos.")


def main():
    print(f"Hola, soy {ASSISTANT_NAME}, el asistente de Rodados Sur.")
    print("Escribe 'salir' para terminar.")
    # La memoria de la conversación: empieza solo con las instrucciones y crece en cada turno.
    messages = [{"role": "system", "content": build_system_prompt()}]
    history = []
    while True:
        message = get_user_input()
        if message.strip().lower() == "salir":
            break
        # Validación del mensaje vacío: antes estaba en call_ai_model.
        if not message.strip():
            print(f"{ASSISTANT_NAME}: Error controlado: el mensaje no puede estar vacío.")
            continue
        # Anotamos dónde empieza este turno, por si hay que deshacerlo.
        start = len(messages)
        # La consulta del cliente entra a la memoria con el rol "user".
        messages.append({"role": "user", "content": message})
        try:
            answer = run_agent(messages)
        except (ValueError, ConnectionError, MissingAPIKeyError) as error:
            # Si algo falló a mitad de camino, borramos los mensajes de este turno: así la memoria
            # no queda con un pedido de herramienta sin respuesta (la API lo rechazaría después).
            del messages[start:]
            print(f"{ASSISTANT_NAME}: Error controlado: {error}")
            continue
        # history cuenta solo las consultas respondidas (para la despedida).
        history.append(message)
        print(f"{ASSISTANT_NAME}: {answer}")
    print(f"{ASSISTANT_NAME}: ¡Hasta luego! Consultas respondidas hoy: {len(history)}.")


if __name__ == "__main__":
    main()
