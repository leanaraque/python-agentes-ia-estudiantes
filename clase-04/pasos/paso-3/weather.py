import os

import requests
from dotenv import load_dotenv

load_dotenv()

URL = "https://api.open-meteo.com/v1/forecast"


def get_weather_report():
    """Consulta Open-Meteo y devuelve un texto con el clima de hoy."""
    latitude = os.getenv("WEATHER_LATITUDE")
    longitude = os.getenv("WEATHER_LONGITUDE")
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
    try:
        response = requests.get(URL, params=params, timeout=10)
        response.raise_for_status()
    except requests.exceptions.RequestException as exc:
        raise ConnectionError(f"no pude consultar el clima ({exc}).") from exc

    data = response.json()
    temperature = data["current"]["temperature_2m"]
    rain_probability = data["daily"]["precipitation_probability_max"][0]

    if rain_probability >= 50:
        advice = "Mejor dejar la bici para otro día."
    else:
        advice = "Buen día para salir a rodar."
    return f"Ahora hay {temperature} °C. Probabilidad de lluvia hoy: {rain_probability} %. {advice}"


if __name__ == "__main__":
    print(get_weather_report())
