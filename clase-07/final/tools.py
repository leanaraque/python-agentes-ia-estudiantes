# tools.py: las herramientas del agente. Son funciones comunes de Python más una descripción
# (TOOLS) que el modelo lee para saber qué puede pedir.
import json
from datetime import datetime

from weather import get_weather_report

# Archivos de datos, en la misma carpeta que tools.py.
ORDERS_FILE = "ordenes.json"
HANDOFFS_FILE = "derivaciones.json"

# La "ficha" de cada herramienta, en el formato que entiende la API (el mismo que muestra el material):
# name (cómo se llama), description (para qué sirve: el modelo decide con esto) y parameters
# (qué datos necesita, descriptos con JSON Schema: tipo, descripción y cuáles son obligatorios).
TOOLS = [
    {
        "type": "function",
        "function": {
            "name": "get_order_status",
            "description": "Consulta el estado de una orden de reparación del taller a partir de su número.",
            "parameters": {
                "type": "object",
                "properties": {
                    "order_id": {"type": "string", "description": "Número de la orden, por ejemplo 1042."},
                },
                "required": ["order_id"],
            },
        },
    },
    {
        "type": "function",
        "function": {
            "name": "get_weather",
            "description": "Consulta el clima de hoy en el barrio de Rodados Sur.",
            # Sin parámetros: el clima no necesita datos de entrada.
            "parameters": {"type": "object", "properties": {}},
        },
    },
    {
        "type": "function",
        "function": {
            "name": "hand_off_to_marta",
            "description": "Deriva la consulta a Marta, la dueña, cuando no hay información para responder o el caso es urgente.",
            "parameters": {
                "type": "object",
                "properties": {
                    "reason": {"type": "string", "description": "Resumen breve de la consulta del cliente."},
                    # enum: los únicos valores permitidos (como LEVELS en la Clase 4).
                    "urgency": {"type": "string", "enum": ["alta", "media", "baja"]},
                },
                "required": ["reason", "urgency"],
            },
        },
    },
]


def get_order_status(order_id):
    """Busca una orden en ordenes.json y devuelve sus datos como texto JSON."""
    # json.load (sin "s") lee un archivo JSON y lo convierte en dict.
    with open(ORDERS_FILE, encoding="utf-8") as file:
        orders = json.load(file)
    # Las claves del JSON son texto: str() por si el número llega como int. .get devuelve None si no existe.
    order = orders.get(str(order_id))
    if order is None:
        return json.dumps({"error": f"No existe la orden {order_id}."}, ensure_ascii=False)
    # El resultado de una herramienta vuelve al modelo como TEXTO: json.dumps convierte el dict en texto JSON.
    return json.dumps(order, ensure_ascii=False)


def get_weather():
    """Devuelve el clima de hoy como texto, o un aviso si no se pudo consultar."""
    # Reutilizamos weather.py de la Clase 2. Si falla, devolvemos el aviso como texto en lugar de
    # cortar el programa: el modelo lo lee y se lo explica al cliente.
    try:
        return get_weather_report()
    except (ValueError, ConnectionError) as error:
        return f"No se pudo consultar el clima: {error}"


def hand_off_to_marta(reason, urgency):
    """Guarda la derivación en derivaciones.json y devuelve una confirmación."""
    # Esta herramienta no solo consulta: ACTÚA (deja registrada la derivación para Marta).
    # La primera vez el archivo no existe: FileNotFoundError, y empezamos con una lista vacía.
    try:
        with open(HANDOFFS_FILE, encoding="utf-8") as file:
            handoffs = json.load(file)
    except FileNotFoundError:
        handoffs = []
    handoffs.append({
        "fecha": datetime.now().strftime("%Y-%m-%d %H:%M"),
        "motivo": reason,
        "urgencia": urgency,
    })
    # "w" reescribe el archivo completo con la lista actualizada.
    with open(HANDOFFS_FILE, "w", encoding="utf-8") as file:
        json.dump(handoffs, file, indent=4, ensure_ascii=False)
    return f"Derivación registrada con urgencia {urgency}. Marta se va a comunicar con el cliente."


def execute_tool(name, arguments):
    """Ejecuta la herramienta pedida por el modelo. arguments llega como texto JSON."""
    # El modelo manda los argumentos como texto JSON, por ejemplo '{"order_id": "1043"}'.
    # json.loads los convierte en dict. "or" usa "{}" si llegaron vacíos.
    args = json.loads(arguments or "{}")
    if name == "get_order_status":
        return get_order_status(args["order_id"])
    if name == "get_weather":
        return get_weather()
    if name == "hand_off_to_marta":
        return hand_off_to_marta(args["reason"], args["urgency"])
    # Si el modelo pide algo que no existe, se lo decimos (no cortamos el programa).
    return f"Herramienta desconocida: {name}."


# Prueba sin modelo: ejecutamos las herramientas "a mano", como lo hará el agente.
if __name__ == "__main__":
    print(execute_tool("get_order_status", '{"order_id": "1043"}'))
    print(execute_tool("get_order_status", '{"order_id": "9999"}'))
    print(execute_tool("get_weather", "{}"))
    print(execute_tool("hand_off_to_marta", '{"reason": "Prueba de derivación", "urgency": "baja"}'))
