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
print(response.status_code)
print(response.url)

data = response.json()
print(type(data))
print(data["current"]["temperature_2m"])
print(data["daily"]["precipitation_probability_max"][0])
