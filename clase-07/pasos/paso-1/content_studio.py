import json
import os
from datetime import datetime

from assistant import FAQ
from llm_client import MissingAPIKeyError, call_language_model, parse_json

PROMOS_DIR = "promos"
REQUIRED_FIELDS = ["titulo", "slogan", "narracion", "descripcion_visual"]
SYSTEM_PROMPT = "Eres el redactor publicitario de Rodados Sur. Respondes solo con un JSON válido, sin texto alrededor."


def build_promo_prompt(topic):
    """Arma el pedido de la promo: el tema, los datos reales del negocio y las reglas de cada campo."""
    business_info = ""
    for answer in FAQ.values():
        business_info += f"- {answer}\n"
    return f"""Escribe una promo corta de Rodados Sur, una tienda y taller de bicicletas de barrio. Tema: {topic}.

### Información del negocio
{business_info}
### Reglas
- Usa solo la información del negocio: no inventes precios, descuentos, fechas ni productos.
- titulo: hasta 40 caracteres.
- slogan: una frase de hasta 70 caracteres.
- narracion: entre 25 y 45 palabras, para leer en voz alta en unos 15 segundos. Texto plano; los precios con la palabra pesos.
- descripcion_visual: la escena para generar la imagen con IA (lugar, personas, luz y estilo), en una o dos oraciones. Sin textos, letras ni logos dentro de la imagen.

Responde solo con un JSON con las claves titulo, slogan, narracion y descripcion_visual."""


def validate_script(script):
    """Comprueba que el guion tenga los cuatro campos con texto. Si falta alguno, lanza ValueError."""
    for field in REQUIRED_FIELDS:
        value = script.get(field)
        if not isinstance(value, str) or not value.strip():
            raise ValueError(f"al guion le falta el campo {field}.")
    return script


def write_promo_script(topic):
    """Pide al modelo el guion de la promo en JSON y lo devuelve validado (un dict)."""
    text = call_language_model(build_promo_prompt(topic), SYSTEM_PROMPT, temperature=0.8)
    return validate_script(parse_json(text))


def create_promo_folder():
    """Crea una carpeta nueva para la promo, con la fecha y la hora en el nombre."""
    folder = os.path.join(PROMOS_DIR, datetime.now().strftime("%Y%m%d_%H%M%S"))
    os.makedirs(folder, exist_ok=True)
    return folder


def save_json(data, path):
    """Guarda un dict como archivo JSON legible (con tildes y sangría)."""
    with open(path, "w", encoding="utf-8") as file:
        json.dump(data, file, ensure_ascii=False, indent=2)
    return path


def main():
    print("Estudio de contenido de Rodados Sur")
    topic = input("¿Sobre qué es la promo?: ").strip()
    if not topic:
        print("Error controlado: el tema no puede estar vacío.")
        return
    try:
        script = write_promo_script(topic)
    except (ValueError, ConnectionError, MissingAPIKeyError) as error:
        print(f"Error controlado: {error}")
        return
    folder = create_promo_folder()
    save_json(script, os.path.join(folder, "guion.json"))
    print(json.dumps(script, ensure_ascii=False, indent=2))
    print(f"Guion guardado en {folder}")


if __name__ == "__main__":
    main()
