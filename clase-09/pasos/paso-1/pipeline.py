import json
import logging
import os
import time
from datetime import datetime

from assistant import ASSISTANT_NAME, FAQ
from llm_client import MissingAPIKeyError, call_language_model_json
from weather import get_weather_report

QUERIES_FILE = "consultas_del_dia.json"
REPORTS_DIR = "reportes"
LOG_FILE = "pipeline.log"
MAX_LENGTH = 500
INTENTS = ("horario", "direccion", "precios", "taller", "alquiler", "clima", "otro")
LEVELS = ("alta", "media", "baja")

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s %(levelname)s %(message)s",
    datefmt="%Y-%m-%d %H:%M:%S",
    handlers=[logging.FileHandler(LOG_FILE, encoding="utf-8"), logging.StreamHandler()],
)


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


def count_by(results, key):
    """Cuenta cuántos resultados hay con cada valor de una clave (por ejemplo, cuántos de cada estado)."""
    counts = {}
    for result in results:
        value = result.get(key)
        if value:
            counts[value] = counts.get(value, 0) + 1
    return counts


def create_report_folder():
    """Crea una carpeta nueva para el reporte, con la fecha y la hora en el nombre."""
    folder = os.path.join(REPORTS_DIR, datetime.now().strftime("%Y%m%d_%H%M%S"))
    os.makedirs(folder, exist_ok=True)
    return folder


def save_json(data, path):
    """Guarda datos como archivo JSON legible (con tildes y sangría)."""
    with open(path, "w", encoding="utf-8") as file:
        json.dump(data, file, ensure_ascii=False, indent=2)
    return path


def run_pipeline(queries):
    """Pasa todas las consultas por la línea, mide los tiempos y guarda el reporte. Devuelve resultados y metadatos."""
    logging.info(f"Inicio: {len(queries)} consultas")
    start = time.perf_counter()
    results = []
    for query in queries:
        query_start = time.perf_counter()
        result = process_query(query)
        result["segundos"] = round(time.perf_counter() - query_start, 2)
        results.append(result)
        if result["estado"] in ("inválida", "error"):
            logging.warning(f"Consulta {result['id']}: {result['estado']} - {result['detalle']}")
        else:
            logging.info(f"Consulta {result['id']}: {result['estado']} ({result['intencion']}) en {result['segundos']} s")
    folder = create_report_folder()
    metadata = {
        "fecha": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        "proveedor": os.getenv("LLM_PROVIDER", "groq"),
        "modelo": os.getenv("GROQ_MODEL", "openai/gpt-oss-20b"),
        "total": len(results),
        "por_estado": count_by(results, "estado"),
        "por_intencion": count_by(results, "intencion"),
        "segundos": round(time.perf_counter() - start, 2),
        "carpeta": folder,
    }
    save_json(results, os.path.join(folder, "resultados.json"))
    save_json(metadata, os.path.join(folder, "metadatos.json"))
    logging.info(f"Fin: {len(results)} consultas en {metadata['segundos']} s. Reporte en {folder}")
    return results, metadata


def print_summary(results, metadata):
    """Muestra el resumen del día para Marta: cuántas de cada estado y cuáles tiene que mirar ella."""
    counts = metadata["por_estado"]
    print("\nResumen del día")
    print(f"- Listas para enviar: {counts.get('lista', 0)}")
    print(f"- Para Marta: {counts.get('para Marta', 0)}")
    print(f"- Inválidas: {counts.get('inválida', 0)}")
    print(f"- Con error: {counts.get('error', 0)}")
    print("Para Marta:")
    for result in results:
        if result["estado"] == "para Marta":
            print(f"  [{result['id']}] {result['canal']}: {result['mensaje']}")


def main():
    print("Pipeline de consultas de Rodados Sur")
    try:
        queries = load_queries(QUERIES_FILE)
        results, metadata = run_pipeline(queries)
    except (OSError, ValueError, MissingAPIKeyError) as error:
        logging.error(f"Error controlado: {error}")
        return
    print_summary(results, metadata)


if __name__ == "__main__":
    main()
