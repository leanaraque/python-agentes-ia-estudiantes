# assistant.py - versión final de la Clase 3.
# Etapa 2 del Proyecto Integrador: el asistente responde con un modelo de lenguaje real (Groq)
# a través de llm_client.py, con un prompt armado a partir del FAQ. El clima sigue con weather.py.
# os viene con Python: permite leer variables de entorno.
import os

# dotenv se instala en el entorno virtual (paquete python-dotenv): lee el archivo .env.
from dotenv import load_dotenv

# Nuestros propios módulos: tienen que estar en la misma carpeta. Se importan sin ".py".
# De llm_client traemos la función y el error propio (para poder atraparlo en main).
from llm_client import MissingAPIKeyError, call_language_model
from weather import get_weather_report

# Carga el .env como variables de entorno. Va antes de cualquier os.getenv.
load_dotenv()

# El nombre ya no está en el código: sale del .env. Si falta, se usa "Asistente".
ASSISTANT_NAME = os.getenv("ASSISTANT_NAME", "Asistente")

# El FAQ de la Clase 1 ya no se usa para buscar palabras: ahora es el CONTEXTO del prompt.
FAQ = {
    "horario": "Abrimos de lunes a viernes de 9 a 13 y de 16 a 20, y los sábados de 9 a 13.",
    "dirección": "Estamos en Av. del Sur 1234.",
    "service": "El service básico cuesta $25.000 y el completo $45.000.",
    "demora": "El taller entrega las bicicletas en 48 horas hábiles.",
    "alquiler": "Alquilamos bicicletas urbanas a $8.000 por día.",
}


# Arma el prompt de sistema a partir del FAQ: si Marta cambia un precio en el FAQ,
# el modelo lo sabe sin tocar el texto del prompt.
def build_system_prompt():
    """Arma las instrucciones para el modelo con la información del FAQ."""
    business_info = ""
    # .values() recorre solo las respuestas del dict (sin las claves).
    for answer in FAQ.values():
        # += agrega texto al final. \n es un salto de línea: cada dato queda en su renglón.
        business_info += f"- {answer}\n"
    # f-string de varias líneas (triples comillas): mete el nombre y la información en el texto.
    return f"""Eres {ASSISTANT_NAME}, el asistente virtual de Rodados Sur, una tienda y taller de bicicletas de barrio.

Tu tarea es responder las consultas de los clientes sobre el negocio.

### Información del negocio
{business_info}
### Reglas
- Responde solo con la información del negocio. Si no la tienes, di que se lo pasas a Marta, la dueña.
- No inventes precios, horarios ni datos.
- Responde en español, con tono cordial, en un máximo de 3 oraciones."""


# def define una función: le da un nombre a un bloque de código para usarlo cuando queramos.
# Los paréntesis vacíos indican que esta función no necesita recibir nada.
# Definir una función NO la ejecuta: solo se ejecuta cuando alguien la llama.
def get_user_input():
    # El texto entre triple comilla es un docstring: documenta qué hace la función.
    # VS Code lo muestra al pasar el mouse sobre el nombre de la función.
    """Pide un mensaje por consola y lo devuelve."""
    # return devuelve un valor a quien llamó a la función y la termina.
    return input("Tú: ")


# Dos líneas en blanco entre funciones: convención de estilo de Python (PEP 8).
# prompt es un parámetro: el nombre que recibe, adentro de la función, el valor que le pasen.
# Cuando main hace call_ai_model(message), el contenido de message llega como prompt.
def call_ai_model(prompt):
    """Responde la consulta: el clima con weather.py; todo lo demás, con el modelo de lenguaje."""
    # Normalizamos: sin espacios en los bordes y en minúsculas (solo para validar y buscar el clima).
    text = prompt.strip().lower()
    # Validación: un mensaje vacío es un error. Lo avisamos con raise.
    if not text:
        raise ValueError("el mensaje no puede estar vacío.")
    # El clima lo sigue resolviendo weather.py: el modelo no sabe qué tiempo hace hoy.
    # (En la Clase 5, el agente va a decidir solo cuándo usar esta herramienta.)
    if "clima" in text or "llueve" in text or "lluvia" in text:
        return get_weather_report()
    # Todo lo demás lo responde el modelo, con el prompt del negocio.
    # Se envía el mensaje original (prompt), no el pasado a minúsculas.
    return call_language_model(prompt, build_system_prompt())


# main es "la función principal": ordena el recorrido completo del programa.
# El nombre main es una convención, no una palabra reservada de Python.
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
