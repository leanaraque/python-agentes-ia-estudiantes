# guardar_clima.py: desafío extra (Laboratorio del Módulo 1, ejercicio 5).
# Guarda la respuesta completa de la API en un archivo JSON cuyo nombre incluye la fecha.
# json viene con Python: convierte entre dict y texto JSON.
import json
# datetime viene con Python: fechas y horas.
from datetime import datetime

import requests

URL = "https://api.open-meteo.com/v1/forecast"

params = {
    "latitude": -34.61,
    "longitude": -58.38,
    "current": "temperature_2m",
    "daily": "precipitation_probability_max",
    "timezone": "America/Argentina/Buenos_Aires",
    "forecast_days": 1,
}

response = requests.get(URL, params=params, timeout=10)
# Si la API devolvió un error, cortamos acá: no tiene sentido guardar una respuesta fallida.
response.raise_for_status()

# strftime da formato a la fecha: %Y año, %m mes, %d día. Queda, por ejemplo, 2026-09-28.
today = datetime.now().strftime("%Y-%m-%d")
file_name = f"clima_{today}.json"
# with abre el archivo y lo cierra solo al terminar el bloque, aunque haya un error.
# "w" = escribir (si existe, lo reemplaza). encoding="utf-8" para que los acentos se guarden bien.
with open(file_name, "w", encoding="utf-8") as file:
    # json.dump escribe el dict como JSON. indent=4 lo deja legible;
    # ensure_ascii=False guarda "°" y los acentos tal cual, en lugar de códigos como °.
    json.dump(response.json(), file, indent=4, ensure_ascii=False)

print(f"Respuesta guardada en {file_name}")
