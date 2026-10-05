# assistant.py - versión final de la Clase 4.
# El modelo analiza cada consulta y responde en JSON (intención, urgencia, confianza, respuesta).
# Python valida ese JSON y decide: clima con weather.py, DESCONOCIDO a Marta, aviso si es urgente.
# os viene con Python: permite leer variables de entorno.
import os

# dotenv se instala en el entorno virtual (paquete python-dotenv): lee el archivo .env.
from dotenv import load_dotenv

# Nuestros propios módulos: tienen que estar en la misma carpeta. Se importan sin ".py".
# De llm_client traemos la función que devuelve un dict (JSON) y el error propio.
from llm_client import MissingAPIKeyError, call_language_model_json
from weather import get_weather_report

# Carga el .env como variables de entorno. Va antes de cualquier os.getenv.
load_dotenv()

# El nombre sale del .env. Si falta, se usa "Asistente".
ASSISTANT_NAME = os.getenv("ASSISTANT_NAME", "Asistente")

# El FAQ sigue siendo el CONTEXTO del prompt.
FAQ = {
    "horario": "Abrimos de lunes a viernes de 9 a 13 y de 16 a 20, y los sábados de 9 a 13.",
    "dirección": "Estamos en Av. del Sur 1234.",
    "service": "El service básico cuesta $25.000 y el completo $45.000.",
    "demora": "El taller entrega las bicicletas en 48 horas hábiles.",
    "alquiler": "Alquilamos bicicletas urbanas a $8.000 por día.",
}

# Tuplas (entre paréntesis): listas que no se modifican. Son los únicos valores que aceptamos.
# Sin tildes a propósito: así comparamos texto exacto sin problemas de acentos.
INTENTS = ("horario", "direccion", "precios", "taller", "alquiler", "clima", "otro")
LEVELS = ("alta", "media", "baja")


# Arma el prompt: rol, contexto (el FAQ), reglas (DESCONOCIDO, clima, urgencia), formato JSON y un ejemplo.
def build_system_prompt():
    """Arma las instrucciones para el modelo con la información del FAQ y el formato JSON."""
    business_info = ""
    for answer in FAQ.values():
        business_info += f"- {answer}\n"
    # En una f-string, las llaves dobles {{ }} se muestran como llaves simples { } en el texto.
    # Hacen falta porque el JSON de ejemplo tiene llaves y la f-string las usa para variables.
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


# Validación del contenido: el JSON puede ser válido y aun así traer valores que no esperamos.
def validate_analysis(data):
    """Comprueba que el análisis tenga todas las claves y valores permitidos."""
    # isinstance(valor, tipo) da True si el valor es de ese tipo.
    if not isinstance(data, dict):
        raise ValueError("el análisis no es un objeto JSON.")
    # in sobre un dict pregunta si existe esa CLAVE.
    for key in ("intencion", "urgencia", "confianza", "respuesta"):
        if key not in data:
            raise ValueError(f"al análisis le falta la clave '{key}'.")
    # not in sobre una tupla: el valor no está entre los permitidos.
    if data["intencion"] not in INTENTS:
        raise ValueError(f"intención desconocida: {data['intencion']}.")
    if data["urgencia"] not in LEVELS or data["confianza"] not in LEVELS:
        raise ValueError("urgencia o confianza con un valor no permitido.")
    return data


# def define una función: le da un nombre a un bloque de código para usarlo cuando queramos.
# Los paréntesis vacíos indican que esta función no necesita recibir nada.
def get_user_input():
    """Pide un mensaje por consola y lo devuelve."""
    return input("Tú: ")


# El corazón de Rayo: pide el análisis al modelo, lo valida y decide qué responder.
def call_ai_model(prompt):
    """Analiza la consulta con el modelo y decide qué responder."""
    if not prompt.strip():
        raise ValueError("el mensaje no puede estar vacío.")
    # Dos pasos en una línea: el modelo devuelve un dict y validate_analysis lo revisa.
    # Si algo no cumple el formato, se lanza ValueError y main lo muestra como error controlado.
    analysis = validate_analysis(call_language_model_json(prompt, build_system_prompt()))
    # Ya no buscamos las palabras "clima" o "lluvia": el MODELO detecta la intención.
    if analysis["intencion"] == "clima":
        return get_weather_report()
    # Patrón DESCONOCIDO: si el modelo no tiene el dato (o no está seguro), no inventa: deriva a Marta.
    if analysis["respuesta"] == "DESCONOCIDO" or analysis["confianza"] == "baja":
        return "No tengo ese dato. Se lo paso a Marta para que te responda."
    # Con datos estructurados, el programa puede DECIDIR: si es urgente, avisa que Marta contacta hoy.
    if analysis["urgencia"] == "alta":
        return analysis["respuesta"] + " Como es urgente, Marta te va a contactar hoy."
    return analysis["respuesta"]


def main():
    print(f"Hola, soy {ASSISTANT_NAME}, el asistente de Rodados Sur.")
    print("Escribe 'salir' para terminar.")
    # history ahora vive adentro de main: es una variable local
    # (solo existe mientras main se ejecuta y no se ve desde otras funciones).
    history = []
    while True:
        # Llamamos a la función: los paréntesis son los que la ejecutan.
        message = get_user_input()
        # .strip() también acá: "salir " con un espacio al final también corta.
        if message.strip().lower() == "salir":
            break
        # try: "intenta" ejecutar este bloque. Si adentro ocurre un error, salta al except.
        try:
            answer = call_ai_model(message)
        # except atrapa solo los tipos de error indicados. ValueError: mensaje vacío, falta configuración
        # o respuesta inválida del modelo. ConnectionError: falló la red o la API (401, 429...).
        # MissingAPIKeyError: falta GROQ_API_KEY en el .env. Otro error seguiría cortando el programa.
        # "as error" guarda el error en una variable; al imprimirla se ve su mensaje.
        except (ValueError, ConnectionError, MissingAPIKeyError) as error:
            print(f"{ASSISTANT_NAME}: Error controlado: {error}")
            # continue salta a la próxima vuelta del while: no guarda el mensaje ni imprime respuesta.
            continue
        history.append(message)
        print(f"{ASSISTANT_NAME}: {answer}")
    print(f"{ASSISTANT_NAME}: ¡Hasta luego! Consultas respondidas hoy: {len(history)}.")


# __name__ vale "__main__" solo cuando ejecutamos este archivo directamente (python assistant.py).
# Si otro archivo lo importa (lo haremos en la Clase 3), main() no se ejecuta sola.
# Sin estas dos líneas, el archivo definiría las funciones pero no haría nada.
if __name__ == "__main__":
    main()
