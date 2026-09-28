# assistant.py - versión final de la Clase 2.
# Etapa 1 del Proyecto Integrador completa: entorno virtual, nombre en variable de entorno,
# función que simula al modelo, errores controlados. Además, responde el clima con una API real.
# os viene con Python: permite leer variables de entorno.
import os

# dotenv se instala en el entorno virtual (paquete python-dotenv): lee el archivo .env.
from dotenv import load_dotenv

# Nuestro propio módulo: weather.py tiene que estar en la misma carpeta. Se importa sin ".py".
from weather import get_weather_report

# Carga el .env como variables de entorno. Va antes de cualquier os.getenv.
load_dotenv()

# El nombre ya no está en el código: sale del .env. Si falta, se usa "Asistente".
ASSISTANT_NAME = os.getenv("ASSISTANT_NAME", "Asistente")

FAQ = {
    "horario": "Abrimos de lunes a viernes de 9 a 13 y de 16 a 20, y los sábados de 9 a 13.",
    "dirección": "Estamos en Av. del Sur 1234.",
    "service": "El service básico cuesta $25.000 y el completo $45.000.",
    "demora": "El taller entrega las bicicletas en 48 horas hábiles.",
    "alquiler": "Alquilamos bicicletas urbanas a $8.000 por día.",
}


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
    """Simula al modelo de lenguaje: busca una palabra clave del FAQ en el mensaje."""
    # .strip() quita espacios al principio y al final; .lower() pasa todo a minúsculas.
    # Se pueden encadenar: primero se aplica strip y sobre ese resultado, lower.
    text = prompt.strip().lower()
    # not text es True cuando text está vacío: un str vacío "" cuenta como falso para Python.
    # Por eso se valida después de strip(): "   " (solo espacios) queda "" y también se detecta.
    if not text:
        # raise lanza (provoca) un error a propósito para avisar que algo salió mal.
        # ValueError es el tipo de error de Python para "el valor recibido no sirve".
        # El texto entre paréntesis es el mensaje que va a ver quien atrape el error.
        # Después de un raise, la función se corta: no sigue al for.
        raise ValueError("el mensaje no puede estar vacío.")
    # Regla del clima, antes del FAQ: si la consulta lo menciona, le preguntamos a la API.
    # "or" da True si al menos una condición es verdadera.
    if "clima" in text or "llueve" in text or "lluvia" in text:
        return get_weather_report()
    for keyword, answer in FAQ.items():
        if keyword in text:
            # Este return termina la función en la primera coincidencia: el for no sigue.
            return answer
    # Solo llega hasta acá si el for terminó sin encontrar ninguna palabra clave.
    return "Todavía no sé responder eso. Se lo paso a Marta."


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
        # except atrapa solo los tipos de error indicados. ValueError: mensaje vacío o falta
        # configuración en el .env. ConnectionError: falló la red o la API del clima.
        # Otro tipo de error seguiría cortando el programa: no ocultamos errores inesperados.
        # "as error" guarda el error en una variable; al imprimirla se ve su mensaje.
        except (ValueError, ConnectionError) as error:
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
