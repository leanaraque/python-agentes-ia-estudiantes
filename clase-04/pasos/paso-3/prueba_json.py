import json

from llm_client import call_language_model

SYSTEM_PROMPT = """Eres el clasificador de consultas de Rodados Sur, un taller de bicicletas.

Responde ÚNICAMENTE con un objeto JSON válido, sin texto antes ni después, con este formato:
{"intencion": "horario | precios | taller | alquiler | clima | otro", "urgencia": "alta | media | baja"}"""

text = call_language_model("Se me rompió la cadena y la necesito mañana para ir a trabajar.", SYSTEM_PROMPT)
print(text)
print(type(text))

data = json.loads(text)
print(type(data))
print(data["intencion"], data["urgencia"])
