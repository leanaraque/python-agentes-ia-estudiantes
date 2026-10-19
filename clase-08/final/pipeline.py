# pipeline.py, paso 2: al pipeline se suma el registro, la última etapa de todo pipeline.
# Cada paso queda escrito en pipeline.log (logging), se mide cuánto tarda cada consulta
# y cada ejecución deja su reporte en reportes/fecha_hora: resultados.json y metadatos.json.
import json
# logging: la forma profesional de dejar registro de lo que pasa (mejor que print):
# cada línea lleva fecha, hora y nivel (INFO, WARNING, ERROR) y puede ir a un archivo.
import logging
import os
# time: para medir cuánto tarda cada consulta (time.perf_counter es un cronómetro).
import time
# datetime: la fecha y la hora, para el nombre de la carpeta del reporte (como las promos).
from datetime import datetime

# Del asistente reusamos el nombre y los datos del negocio (el FAQ).
# Importar assistant.py no arranca el chat: main() solo corre si se ejecuta ese archivo.
from assistant import ASSISTANT_NAME, FAQ
# De la Clase 4: call_language_model_json pide una respuesta en JSON y la convierte en dict
# (si llega mal, pide que la corrija una vez).
from llm_client import MissingAPIKeyError, call_language_model_json
# De la Clase 2: el clima real desde Open-Meteo, para las consultas sobre el clima.
from weather import get_weather_report

# El archivo con las consultas del día. En la vida real llegarían de WhatsApp o de la web;
# acá las juntamos en un JSON para procesarlas todas de una vez (en lote).
QUERIES_FILE = "consultas_del_dia.json"
# Cada ejecución guarda su reporte en reportes/fecha_hora.
REPORTS_DIR = "reportes"
# El registro de todas las ejecuciones: el archivo crece, no se borra (como el de un servidor).
LOG_FILE = "pipeline.log"
# Largo máximo de un mensaje. Uno más largo se rechaza sin gastar una llamada al modelo.
MAX_LENGTH = 500
# Los valores permitidos, los mismos de la Clase 4. Son tuplas: listas que no cambian.
INTENTS = ("horario", "direccion", "precios", "taller", "alquiler", "clima", "otro")
LEVELS = ("alta", "media", "baja")

# Configuración del registro, una sola vez, al cargar el archivo:
# level=INFO: guarda INFO, WARNING y ERROR (no los mensajes de depuración, DEBUG).
# format: fecha y hora, nivel y mensaje. datefmt: cómo se escribe la fecha.
# handlers: a dónde va cada línea. FileHandler, al archivo pipeline.log;
# StreamHandler, a la terminal. Las dos cosas a la vez.
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s %(levelname)s %(message)s",
    datefmt="%Y-%m-%d %H:%M:%S",
    handlers=[logging.FileHandler(LOG_FILE, encoding="utf-8"), logging.StreamHandler()],
)


# Etapa 1, ENTRADA: leer los datos. Si el archivo no existe da OSError;
# si el JSON está mal escrito, ValueError. Los dos se atrapan en main().
def load_queries(path):
    """Entrada: lee las consultas del día desde un archivo JSON (una lista de dicts)."""
    with open(path, encoding="utf-8") as file:
        queries = json.load(file)
    # isinstance comprueba el tipo: esperamos una lista de consultas, no otra cosa.
    if not isinstance(queries, list):
        raise ValueError(f"{path} no tiene una lista de consultas.")
    return queries


# Etapa 2, VALIDACIÓN: Python revisa cada consulta ANTES de llamar al modelo.
# Lo que no sirve se rechaza gratis y al instante: no gasta tokens ni tiempo.
def validate_query(query):
    """Validación: devuelve el texto de la consulta, sin espacios de más. Si no sirve, lanza ValueError."""
    # .get devuelve None si la clave no está (con query["mensaje"] daría KeyError).
    text = query.get("mensaje")
    # Un audio o una foto de WhatsApp llega sin texto (None): no es texto, no se procesa.
    if not isinstance(text, str):
        raise ValueError("el mensaje no es texto: puede ser un audio o una foto.")
    # strip quita los espacios y saltos de línea del principio y del final.
    text = text.strip()
    if not text:
        raise ValueError("el mensaje está vacío.")
    if len(text) > MAX_LENGTH:
        raise ValueError(f"el mensaje tiene más de {MAX_LENGTH} caracteres.")
    return text


# Las instrucciones de la Clase 4: rol, datos del negocio, reglas y formato JSON.
# Para un lote conviene una sola llamada por consulta: clasificar y escribir el borrador juntos.
def build_classifier_prompt():
    """Arma las instrucciones para clasificar una consulta en JSON (las de la Clase 4)."""
    business_info = ""
    for answer in FAQ.values():
        business_info += f"- {answer}\n"
    # Las llaves dobles {{ }} del final son llaves literales: en un f-string, una sola { abre una variable.
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


# Igual que en la Clase 4: lo que viene del modelo se revisa antes de usarlo.
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


# Etapa 3, MODELO: la única etapa que usa IA. Una llamada a Groq por consulta.
def classify_query(text):
    """Modelo: la IA clasifica la consulta y escribe un borrador de respuesta (un dict validado)."""
    return validate_analysis(call_language_model_json(text, build_classifier_prompt()))


# Etapa 4, DECISIÓN: con lo que dijo la IA, Python aplica las reglas de Marta.
# Las reglas son fijas y se pueden leer en el código; no dependen del modelo.
def decide_status(analysis):
    """Decide qué pasa con la consulta: las reglas del negocio las aplica Python, no la IA."""
    # El clima lo responde Open-Meteo (dato real), así que no hace falta que Marta lo mire.
    if analysis["intencion"] == "clima":
        return "lista"
    # Para Marta: lo que Rayo no sabe (DESCONOCIDO o confianza baja) y lo urgente.
    if analysis["respuesta"] == "DESCONOCIDO" or analysis["confianza"] == "baja" or analysis["urgencia"] == "alta":
        return "para Marta"
    return "lista"


# Una consulta recorre toda la línea. La clave: un error en UNA consulta no corta el pipeline.
# Se marca (inválida o error), se guarda el motivo y se sigue con la siguiente.
def process_query(query):
    """Pasa una consulta por la línea: validación y modelo. Si algo falla, la marca y no corta el resto."""
    # El resultado empieza con los datos de la consulta; después se suman el análisis y el estado.
    result = {"id": query.get("id"), "canal": query.get("canal"), "mensaje": query.get("mensaje")}
    try:
        text = validate_query(query)
    except ValueError as error:
        result["estado"] = "inválida"
        result["detalle"] = str(error)
        return result
    try:
        # Si Groq no responde (sin internet, clave mala, límite 429) llega un ConnectionError;
        # si el JSON no pasa la validación, un ValueError. En los dos casos: estado "error".
        analysis = classify_query(text)
        if analysis["intencion"] == "clima":
            # Para el clima, la respuesta la escribe Python con el dato real (la IA solo clasificó).
            analysis["respuesta"] = get_weather_report()
    except (ValueError, ConnectionError) as error:
        result["estado"] = "error"
        result["detalle"] = str(error)
        return result
    # update copia en result todas las claves del análisis (intencion, urgencia, confianza, respuesta).
    result.update(analysis)
    result["estado"] = decide_status(analysis)
    return result


# Cuenta, por ejemplo, cuántas consultas hay de cada estado: {"lista": 4, "para Marta": 3, ...}.
# counts.get(value, 0) devuelve 0 la primera vez que aparece un valor.
def count_by(results, key):
    """Cuenta cuántos resultados hay con cada valor de una clave (por ejemplo, cuántos de cada estado)."""
    counts = {}
    for result in results:
        value = result.get(key)
        if value:
            counts[value] = counts.get(value, 0) + 1
    return counts


# Cada ejecución deja su carpeta: el historial del pipeline (como promos/ en la Clase 7).
def create_report_folder():
    """Crea una carpeta nueva para el reporte, con la fecha y la hora en el nombre."""
    folder = os.path.join(REPORTS_DIR, datetime.now().strftime("%Y%m%d_%H%M%S"))
    os.makedirs(folder, exist_ok=True)
    return folder


# La misma función de content_studio.py (Clase 7).
def save_json(data, path):
    """Guarda datos como archivo JSON legible (con tildes y sangría)."""
    with open(path, "w", encoding="utf-8") as file:
        json.dump(data, file, ensure_ascii=False, indent=2)
    return path


# La línea completa: todas las consultas, una por una.
def run_pipeline(queries):
    """Pasa todas las consultas por la línea, mide los tiempos y guarda el reporte. Devuelve resultados y metadatos."""
    # logging.info escribe una línea de nivel INFO en la terminal y en pipeline.log.
    logging.info(f"Inicio: {len(queries)} consultas")
    # perf_counter es un cronómetro: se toma al principio y al final, y la resta es el tiempo.
    start = time.perf_counter()
    # Una lista donde se va guardando el resultado de cada consulta.
    results = []
    for query in queries:
        query_start = time.perf_counter()
        result = process_query(query)
        # Cuánto tardó esta consulta, con dos decimales. Las inválidas tardan casi 0: no llamaron al modelo.
        result["segundos"] = round(time.perf_counter() - query_start, 2)
        results.append(result)
        # Lo que salió mal va como WARNING (advertencia): se encuentra rápido en el archivo.
        if result["estado"] in ("inválida", "error"):
            logging.warning(f"Consulta {result['id']}: {result['estado']} - {result['detalle']}")
        else:
            logging.info(f"Consulta {result['id']}: {result['estado']} ({result['intencion']}) en {result['segundos']} s")
    folder = create_report_folder()
    # Los METADATOS: datos sobre la ejecución (cuándo, con qué modelo, cuántas, cuánto tardó).
    # Sirven para comparar días y modelos, y para encontrar problemas después.
    metadata = {
        "fecha": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        # Con qué proveedor y modelo se procesó: si mañana cambia el modelo, se puede comparar.
        "proveedor": os.getenv("LLM_PROVIDER", "groq"),
        "modelo": os.getenv("GROQ_MODEL", "openai/gpt-oss-20b"),
        "total": len(results),
        "por_estado": count_by(results, "estado"),
        "por_intencion": count_by(results, "intencion"),
        "segundos": round(time.perf_counter() - start, 2),
        "carpeta": folder,
    }
    # La ENTREGA: los resultados quedan en un archivo que otro sistema (o la web) puede leer.
    save_json(results, os.path.join(folder, "resultados.json"))
    save_json(metadata, os.path.join(folder, "metadatos.json"))
    logging.info(f"Fin: {len(results)} consultas en {metadata['segundos']} s. Reporte en {folder}")
    # Devuelve dos cosas a la vez (una tupla). Quien llama las recibe así: results, metadata = ...
    return results, metadata


# El resumen para Marta, en la terminal. En el paso 4, lo mismo se ve en la web.
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
    # Estos errores sí detienen todo: sin archivo de consultas o sin clave, no tiene sentido seguir.
    # (MissingAPIKeyError es un tipo de OSError; lo nombramos para que se lea claro.)
    except (OSError, ValueError, MissingAPIKeyError) as error:
        # Los errores que detienen todo también quedan en el registro, con nivel ERROR.
        logging.error(f"Error controlado: {error}")
        return
    print_summary(results, metadata)


if __name__ == "__main__":
    main()
