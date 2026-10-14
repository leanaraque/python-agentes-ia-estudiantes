# weather.py: módulo que consulta el clima y devuelve un texto listo para el asistente.
# Mismo patrón que llm_client.py en la Clase 3: no pide datos (input) ni imprime (print),
# solo recibe, consulta y devuelve. Si algo sale mal, lanza un error para que otro lo maneje.
import os

import requests
from dotenv import load_dotenv

load_dotenv()

URL = "https://api.open-meteo.com/v1/forecast"


def get_weather_report():
    """Consulta Open-Meteo y devuelve un texto con el clima de hoy."""
    # Las coordenadas ahora salen del .env. os.getenv siempre devuelve texto (str) o None.
    latitude = os.getenv("WEATHER_LATITUDE")
    longitude = os.getenv("WEATHER_LONGITUDE")
    # Si falta alguna, avisamos con un mensaje claro en lugar de dejar que la API falle.
    if not latitude or not longitude:
        raise ValueError("faltan WEATHER_LATITUDE y WEATHER_LONGITUDE en el archivo .env.")

    params = {
        "latitude": latitude,
        "longitude": longitude,
        "current": "temperature_2m",
        "daily": "precipitation_probability_max",
        "timezone": "America/Argentina/Buenos_Aires",
        "forecast_days": 1,
    }
    # Todo lo que depende de la red va dentro de try: puede fallar por causas ajenas a nosotros.
    try:
        response = requests.get(URL, params=params, timeout=10)
        # raise_for_status() lanza un error si el código es 4xx (error nuestro, por ejemplo
        # un parámetro mal escrito) o 5xx (error del servidor). Con 200 no hace nada.
        response.raise_for_status()
    # RequestException agrupa todos los errores de requests: sin internet, timeout, 4xx, 5xx.
    except requests.exceptions.RequestException as exc:
        # Lo "traducimos" a ConnectionError, un error general de Python. Así quien use esta
        # función no necesita saber que por dentro usamos requests.
        # "from exc" conserva el error original para poder investigarlo.
        raise ConnectionError(f"no pude consultar el clima ({exc}).") from exc

    data = response.json()
    temperature = data["current"]["temperature_2m"]
    rain_probability = data["daily"]["precipitation_probability_max"][0]

    # La probabilidad es un número (int): se puede comparar con >=.
    if rain_probability >= 50:
        advice = "Mejor dejar la bici para otro día."
    else:
        advice = "Buen día para salir a rodar."
    # f-string: sin la f, se mostraría literalmente {temperature}. Con la f, Python reemplaza
    # cada { } por el valor de la variable.
    return f"Ahora hay {temperature} °C. Probabilidad de lluvia hoy: {rain_probability} %. {advice}"


# Prueba del módulo: solo corre con "python weather.py", no cuando assistant.py lo importa.
if __name__ == "__main__":
    print(get_weather_report())
