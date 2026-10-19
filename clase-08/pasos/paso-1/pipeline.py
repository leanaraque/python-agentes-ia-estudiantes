import json

from assistant import ASSISTANT_NAME, FAQ
from llm_client import MissingAPIKeyError, call_language_model_json
from weather import get_weather_report

QUERIES_FILE = "consultas_del_dia.json"
MAX_LENGTH = 500
INTENTS = ("horario", "direccion", "precios", "taller", "alquiler", "clima", "otro")
LEVELS = ("alta", "media", "baja")


def load_queries(path):
    """Entrada: lee las consultas del día desde un archivo JSON (una lista de dicts)."""
    with open(path, encoding="utf-8") as file:
        queries = json.load(file)
    if not isinstance(queries, list):
        raise ValueError(f"{path} no tiene una lista de consultas.")
    return queries


def validate_query(query):
    """Validación: devuelve el texto de la consulta, sin espacios de más. Si no sirve, lanza ValueError."""
    text = query.get("mensaje")
    if not isinstance(text, str):
        raise ValueError("el mensaje no es texto: puede ser un audio o una foto.")
    text = text.strip()
    if not text:
        raise ValueError("el mensaje está vacío.")
    if len(text) > MAX_LENGTH:
        raise ValueError(f"el mensaje tiene más de {MAX_LENGTH} caracteres.")
    return text


def build_classifier_prompt():
    """Arma las instrucciones para clasificar una consulta en JSON (las de la Clase 4)."""
    business_info = ""
    for answer in FAQ.values():
        business_info += f"- {answer}\n"
    return f"""Eres {ASSISTANT_NAME}, el asistente virtual de Rodados Sur, una tienda y taller de bicicletas de barrio.

Tu tarea es analizar la consulta del cliente y escribir un borrador de respuesta.

### Información del negocio
{business_info}
### Reglas
- Usa solo la información del negocio. Si la respuesta no está ahí, escribe exactamente DESCONOCIDO en "respuesta" y "baja" en "confianza".
- No inventes precios, horarios, productos ni datos.
- Si preguntan por el clima o si conviene salir a andar en bici, la intención es "clima".
- La urgencia es "alta" si el cliente necesita la bicicleta pronto para trabajar o moverse.

### Formato de salida
Responde ÚNICAMENTE con un objeto JSON válido, sin texto antes ni después:
{{"intencion": "horario | direccion | precios | taller | alquiler | clima | otro", "urgencia": "alta | media | baja", "confianza": "alta | media | baja", "respuesta": "texto en español, cordial, máximo 2 oraciones"}}"""


def validate_analysis(data):
    """Comprueba que el análisis tenga todas las claves y valores permitidos (como en la Clase 4)."""
    if not isinstance(data, dict):
        raise ValueError("el análisis no es un objeto JSON.")
    for key in ("intencion", "urgencia", "confianza", "respuesta"):
        if key not in data:
            raise ValueError(f"al análisis le falta la clave '{key}'.")
    if data["intencion"] not in INTENTS:
        raise ValueError(f"intención desconocida: {data['intencion']}.")
    if data["urgencia"] not in LEVELS or data["confianza"] not in LEVELS:
        raise ValueError("urgencia o confianza con un valor no permitido.")
    return data


def classify_query(text):
    """Modelo: la IA clasifica la consulta y escribe un borrador de respuesta (un dict validado)."""
    return validate_analysis(call_language_model_json(text, build_classifier_prompt()))


def decide_status(analysis):
    """Decide qué pasa con la consulta: las reglas del negocio las aplica Python, no la IA."""
    if analysis["intencion"] == "clima":
        return "lista"
    if analysis["respuesta"] == "DESCONOCIDO" or analysis["confianza"] == "baja" or analysis["urgencia"] == "alta":
        return "para Marta"
    return "lista"


def process_query(query):
    """Pasa una consulta por la línea: validación y modelo. Si algo falla, la marca y no corta el resto."""
    result = {"id": query.get("id"), "canal": query.get("canal"), "mensaje": query.get("mensaje")}
    try:
        text = validate_query(query)
    except ValueError as error:
        result["estado"] = "inválida"
        result["detalle"] = str(error)
        return result
    try:
        analysis = classify_query(text)
        if analysis["intencion"] == "clima":
            analysis["respuesta"] = get_weather_report()
    except (ValueError, ConnectionError) as error:
        result["estado"] = "error"
        result["detalle"] = str(error)
        return result
    result.update(analysis)
    result["estado"] = decide_status(analysis)
    return result


def run_pipeline(queries):
    """Pasa todas las consultas por la línea, una por una, y devuelve la lista de resultados."""
    results = []
    for query in queries:
        results.append(process_query(query))
    return results


def main():
    print("Pipeline de consultas de Rodados Sur")
    try:
        queries = load_queries(QUERIES_FILE)
        print(f"Consultas a procesar: {len(queries)}")
        results = run_pipeline(queries)
    except (OSError, ValueError, MissingAPIKeyError) as error:
        print(f"Error controlado: {error}")
        return
    for result in results:
        if result["estado"] in ("inválida", "error"):
            print(f"[{result['id']}] {result['estado']}: {result['detalle']}")
        else:
            print(f"[{result['id']}] {result['estado']} ({result['intencion']}, urgencia {result['urgencia']}): {result['respuesta']}")


if __name__ == "__main__":
    main()
