import json
import os
import textwrap
from datetime import datetime

from moviepy import AudioFileClip, ImageClip
from PIL import Image, ImageDraw, ImageFont, ImageOps

from assistant import FAQ
from llm_client import MissingAPIKeyError, call_language_model, parse_json
from speech_output import save_audio

PROMOS_DIR = "promos"
REQUIRED_FIELDS = ["titulo", "slogan", "narracion", "descripcion_visual"]
SYSTEM_PROMPT = "Eres el redactor publicitario de Rodados Sur. Respondes solo con un JSON válido, sin texto alrededor."
WEB_IMAGE_NAMES = ["imagen.png", "imagen.jpg", "imagen.jpeg", "imagen.webp"]
POSTER_SIZE = (1280, 720)
BRAND_COLOR = "#0B3954"
ACCENT_COLOR = "#FF7F11"


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


def take_web_image(folder):
    """Busca la imagen generada en la web (imagen.png, .jpg, .jpeg o .webp) y la mueve a la carpeta de la promo."""
    for name in WEB_IMAGE_NAMES:
        if os.path.exists(name):
            extension = os.path.splitext(name)[1]
            new_path = os.path.join(folder, "imagen_ia" + extension)
            os.replace(name, new_path)
            return new_path
    return None


def load_font(size, bold=False):
    """Carga la letra Arial de Windows en el tamaño pedido. Si no está, usa la letra de Pillow."""
    try:
        return ImageFont.truetype("arialbd.ttf" if bold else "arial.ttf", size)
    except OSError:
        return ImageFont.load_default(size)


def make_poster(script, image_path, poster_path):
    """Arma el afiche: la imagen a la izquierda (o una placa) y el texto exacto de la promo a la derecha."""
    poster = Image.new("RGB", POSTER_SIZE, BRAND_COLOR)
    draw = ImageDraw.Draw(poster)
    if image_path:
        image = ImageOps.fit(Image.open(image_path).convert("RGB"), (720, 720))
        poster.paste(image, (0, 0))
        draw.rectangle((0, 676, 300, 720), fill="black")
        draw.text((16, 686), "Imagen generada con IA", font=load_font(22), fill="white")
    else:
        draw.rectangle((0, 0, 720, 720), fill=ACCENT_COLOR)
        draw.text((70, 300), "Rodados Sur", font=load_font(100, bold=True), fill=BRAND_COLOR)
    y = 70
    for line in textwrap.wrap(script["titulo"], width=15):
        draw.text((770, y), line, font=load_font(56, bold=True), fill="white")
        y += 66
    y += 30
    for line in textwrap.wrap(script["slogan"], width=26):
        draw.text((770, y), line, font=load_font(34), fill=ACCENT_COLOR)
        y += 44
    draw.text((770, 600), "Rodados Sur", font=load_font(34, bold=True), fill="white")
    draw.text((770, 646), FAQ["dirección"], font=load_font(26), fill="white")
    poster.save(poster_path)
    return poster_path


def make_video(poster_path, audio_path, video_path):
    """Une el afiche y la narración en un video MP4 que dura lo mismo que el audio."""
    audio = AudioFileClip(audio_path)
    video = ImageClip(poster_path).with_duration(audio.duration).with_audio(audio)
    video.write_videofile(video_path, fps=24, codec="libx264", audio_codec="aac", logger=None)
    audio.close()
    video.close()
    return video_path


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

    print("\nLa imagen: copia la descripcion_visual y genérala en ChatGPT, Gemini o Copilot.")
    print("Guárdala en esta carpeta con el nombre imagen (png, jpg o webp).")
    input("Presiona Enter cuando esté (sin imagen, Rayo arma una placa con el título): ")
    image_path = take_web_image(folder)
    poster_file = os.path.join(folder, "afiche.png")
    try:
        poster_path = make_poster(script, image_path, poster_file)
    except OSError as error:
        print(f"Error controlado: no pude abrir la imagen ({error}). Uso la placa.")
        poster_path = make_poster(script, None, poster_file)
    print(f"Afiche guardado en {poster_path}")

    try:
        audio_path = save_audio(script["narracion"], os.path.join(folder, "narracion.mp3"))
    except ConnectionError as error:
        print(f"Error controlado: {error}")
        return
    print(f"Narración guardada en {audio_path}")
    print("Armando el video...")
    video_path = make_video(poster_path, audio_path, os.path.join(folder, "promo.mp4"))
    print(f"Video listo: {video_path}")


if __name__ == "__main__":
    main()
