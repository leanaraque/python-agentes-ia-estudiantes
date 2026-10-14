# content_studio.py, paso 4 (opcional): la imagen también se puede generar por API,
# con FLUX en Cloudflare Workers AI. Sin claves en el .env, todo funciona como en el paso 3.
# base64: convierte texto en bytes y al revés. La API de imágenes devuelve la imagen
# como un texto larguísimo (base64), porque JSON no puede llevar bytes sueltos.
import base64
import json
import os
# textwrap: corta un texto largo en renglones de un ancho máximo (para el afiche).
import textwrap
# datetime: para poner la fecha y la hora en el nombre de la carpeta de cada promo.
from datetime import datetime

# requests: la misma librería de la Clase 2, ahora para pedir la imagen a Cloudflare.
import requests
# MoviePy: edita video con Python. ImageClip convierte una imagen en un video quieto;
# AudioFileClip abre un audio. Por dentro usa FFmpeg, que se instaló con imageio-ffmpeg.
from moviepy import AudioFileClip, ImageClip
# Pillow (se instala como pillow y se importa como PIL) edita imágenes:
# Image crea y abre, ImageDraw dibuja texto y rectángulos, ImageFont carga letras
# e ImageOps.fit recorta una imagen a un tamaño sin deformarla.
from PIL import Image, ImageDraw, ImageFont, ImageOps

# El FAQ de assistant.py: los datos reales del negocio. Si Marta cambia un precio ahí,
# las promos lo usan sin tocar este archivo. (Importar assistant.py no arranca el chat:
# main() solo corre cuando se ejecuta assistant.py directamente.)
from assistant import FAQ
# De la Clase 4: call_language_model para pedir el texto y parse_json para
# sacar el JSON de la respuesta (aunque el modelo agregue texto alrededor).
from llm_client import MissingAPIKeyError, call_language_model, parse_json
# De la Clase 6: save_audio convierte texto en mp3 con la voz de Google (gTTS).
from speech_output import save_audio

# Cada promo se guarda en su propia carpeta dentro de promos/.
PROMOS_DIR = "promos"
# Los cuatro campos que tiene que traer el guion (como intencion y urgencia en la Clase 4).
REQUIRED_FIELDS = ["titulo", "slogan", "narracion", "descripcion_visual"]
# El rol del modelo para esta tarea: redactor, no asistente de clientes.
SYSTEM_PROMPT = "Eres el redactor publicitario de Rodados Sur. Respondes solo con un JSON válido, sin texto alrededor."
# Los nombres que buscamos para la imagen generada en la web (cada sitio descarga en un formato).
WEB_IMAGE_NAMES = ["imagen.png", "imagen.jpg", "imagen.jpeg", "imagen.webp"]
# Tamaño del afiche en píxeles (ancho, alto): 16:9, el formato de un video horizontal.
POSTER_SIZE = (1280, 720)
# Los colores de Rodados Sur, en hexadecimal (como en HTML): azul oscuro y naranja.
BRAND_COLOR = "#0B3954"
ACCENT_COLOR = "#FF7F11"
# La dirección del modelo FLUX.1 schnell en Cloudflare. {account_id} es un hueco
# que se completa con .format() usando el número de cuenta del .env.
IMAGE_API_URL = "https://api.cloudflare.com/client/v4/accounts/{account_id}/ai/run/@cf/black-forest-labs/flux-1-schnell"


def build_promo_prompt(topic):
    """Arma el pedido de la promo: el tema, los datos reales del negocio y las reglas de cada campo."""
    # El mismo armado de la Clase 5: una línea con guion por cada respuesta del FAQ.
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


# Validar lo que devuelve el modelo, como en la Clase 4: nunca confiar a ciegas.
def validate_script(script):
    """Comprueba que el guion tenga los cuatro campos con texto. Si falta alguno, lanza ValueError."""
    for field in REQUIRED_FIELDS:
        value = script.get(field)
        # Falta el campo (None), no es texto, o está vacío: el guion no sirve.
        if not isinstance(value, str) or not value.strip():
            raise ValueError(f"al guion le falta el campo {field}.")
    return script


def write_promo_script(topic):
    """Pide al modelo el guion de la promo en JSON y lo devuelve validado (un dict)."""
    # Temperatura 0.8 (Clase 3): para una promo queremos variedad y creatividad.
    # Para clasificar (Clase 4) usamos 0.1: ahí queríamos siempre la misma respuesta.
    text = call_language_model(build_promo_prompt(topic), SYSTEM_PROMPT, temperature=0.8)
    # parse_json convierte el texto en dict; validate_script revisa los campos.
    # Si algo falla, sube un ValueError que main() muestra como error controlado.
    return validate_script(parse_json(text))


def create_promo_folder():
    """Crea una carpeta nueva para la promo, con la fecha y la hora en el nombre."""
    # strftime arma el nombre con la fecha y la hora, por ejemplo 20261016_193015:
    # así cada promo tiene su carpeta y ninguna pisa a otra.
    # os.path.join pone la barra correcta del sistema (promos\20261016_193015 en Windows).
    folder = os.path.join(PROMOS_DIR, datetime.now().strftime("%Y%m%d_%H%M%S"))
    # Crea la carpeta (y promos/ si no existe). exist_ok=True: si ya existe, no da error.
    os.makedirs(folder, exist_ok=True)
    return folder


def save_json(data, path):
    """Guarda un dict como archivo JSON legible (con tildes y sangría)."""
    # "w": escribir (si el archivo existe, se reemplaza). encoding="utf-8" para las tildes.
    with open(path, "w", encoding="utf-8") as file:
        # ensure_ascii=False guarda "narración" tal cual (sin \u00f3); indent=2 lo deja legible.
        json.dump(data, file, ensure_ascii=False, indent=2)
    return path


# Desafío extra: la imagen por API. Si faltan las claves, devuelve None y main() sigue
# con el camino de la web, así el programa funciona igual para quien no tenga cuenta.
def generate_image(prompt, path):
    """Genera la imagen con FLUX en Cloudflare y la guarda. Si no hay claves en el .env, devuelve None."""
    account_id = os.getenv("CLOUDFLARE_ACCOUNT_ID")
    token = os.getenv("CLOUDFLARE_API_TOKEN")
    if not account_id or not token:
        return None
    url = IMAGE_API_URL.format(account_id=account_id)
    # El mismo encabezado que con Groq (Clase 3): Bearer y la clave.
    headers = {"Authorization": f"Bearer {token}"}
    try:
        # El pedido lleva solo el prompt. FLUX.1 schnell genera la imagen en unos pocos pasos.
        response = requests.post(url, headers=headers, json={"prompt": prompt}, timeout=60)
        response.raise_for_status()
    # Sin internet, clave inválida (401) o cuota diaria agotada: un error controlado.
    except requests.exceptions.RequestException as exc:
        raise ConnectionError(f"no pude generar la imagen ({exc}).") from exc
    try:
        # La respuesta es {"result": {"image": "...base64..."}, "success": true}.
        # b64decode convierte ese texto de vuelta en los bytes de un jpg.
        image_bytes = base64.b64decode(response.json()["result"]["image"])
    except (ValueError, KeyError, TypeError) as exc:
        raise ValueError("el servicio de imágenes devolvió una respuesta con un formato inesperado.") from exc
    # "wb": escribir bytes (una imagen no es texto, como el audio en la Clase 6).
    with open(path, "wb") as file:
        file.write(image_bytes)
    return path


# La imagen se genera fuera de Python (ChatGPT, Gemini o Copilot) y se guarda en la carpeta
# de la clase con el nombre imagen. Esta función la busca y la mueve a la carpeta de la promo.
def take_web_image(folder):
    """Busca la imagen generada en la web (imagen.png, .jpg, .jpeg o .webp) y la mueve a la carpeta de la promo."""
    for name in WEB_IMAGE_NAMES:
        if os.path.exists(name):
            # splitext separa nombre y extensión: ("imagen", ".png"). [1] es la extensión.
            extension = os.path.splitext(name)[1]
            new_path = os.path.join(folder, "imagen_ia" + extension)
            # Mover (no copiar): así la próxima promo no reusa la imagen de esta.
            os.replace(name, new_path)
            return new_path
    # None: no hay imagen. Quien llama a la función decide qué hacer (la placa).
    return None


# Arial viene con Windows. arialbd.ttf es la versión en negrita (bold).
def load_font(size, bold=False):
    """Carga la letra Arial de Windows en el tamaño pedido. Si no está, usa la letra de Pillow."""
    try:
        return ImageFont.truetype("arialbd.ttf" if bold else "arial.ttf", size)
    # OSError: no encontró el archivo de la letra (por ejemplo, en otro sistema operativo).
    # load_default(size) es la letra que trae Pillow, en el tamaño pedido.
    except OSError:
        return ImageFont.load_default(size)


def make_poster(script, image_path, poster_path):
    """Arma el afiche: la imagen a la izquierda (o una placa) y el texto exacto de la promo a la derecha."""
    # Un lienzo vacío de 1280 x 720, pintado con el color de la marca.
    # RGB: colores con rojo, verde y azul (sin transparencia).
    poster = Image.new("RGB", POSTER_SIZE, BRAND_COLOR)
    # draw es el "lápiz" para escribir y dibujar sobre el lienzo.
    draw = ImageDraw.Draw(poster)
    if image_path:
        # Abre la imagen, la pasa a RGB (algunas traen transparencia) y la recorta a 720 x 720
        # desde el centro, sin estirarla. Funciona con png, jpg o webp: Pillow mira el contenido.
        image = ImageOps.fit(Image.open(image_path).convert("RGB"), (720, 720))
        # La pega en la mitad izquierda: (0, 0) es la esquina de arriba a la izquierda.
        poster.paste(image, (0, 0))
        # Ética: marcar el contenido generado. Una franja negra abajo a la izquierda con el aviso.
        # Las coordenadas son (izquierda, arriba, derecha, abajo) en píxeles.
        draw.rectangle((0, 676, 300, 720), fill="black")
        draw.text((16, 686), "Imagen generada con IA", font=load_font(22), fill="white")
    else:
        # Sin imagen: la placa. Un rectángulo naranja con el nombre del negocio.
        # No lleva el aviso de IA porque no hay nada generado con IA.
        draw.rectangle((0, 0, 720, 720), fill=ACCENT_COLOR)
        draw.text((70, 300), "Rodados Sur", font=load_font(100, bold=True), fill=BRAND_COLOR)
    # y es la altura donde va el próximo renglón; baja después de cada uno.
    y = 70
    # El título en renglones de hasta 15 caracteres, en blanco y negrita, a la derecha (x = 770).
    for line in textwrap.wrap(script["titulo"], width=15):
        draw.text((770, y), line, font=load_font(56, bold=True), fill="white")
        # Alto de cada renglón del título: 56 de la letra + 10 de aire.
        y += 66
    # Un espacio extra entre el título y el slogan.
    y += 30
    for line in textwrap.wrap(script["slogan"], width=26):
        draw.text((770, y), line, font=load_font(34), fill=ACCENT_COLOR)
        y += 44
    draw.text((770, 600), "Rodados Sur", font=load_font(34, bold=True), fill="white")
    # La dirección sale del FAQ: un dato exacto, escrito por Python y no inventado por la IA.
    draw.text((770, 646), FAQ["dirección"], font=load_font(26), fill="white")
    # Pillow elige el formato por la extensión del nombre: .png.
    poster.save(poster_path)
    return poster_path


# El video más simple: una imagen fija con la narración de fondo (Laboratorio M5, ejercicio 3).
def make_video(poster_path, audio_path, video_path):
    """Une el afiche y la narración en un video MP4 que dura lo mismo que el audio."""
    audio = AudioFileClip(audio_path)
    # La imagen dura lo mismo que el audio (audio.duration, en segundos) y lleva el audio.
    # MoviePy 2 usa with_...: cada paso devuelve un clip nuevo, no modifica el anterior.
    video = ImageClip(poster_path).with_duration(audio.duration).with_audio(audio)
    # Escribe el MP4: 24 cuadros por segundo, video H.264 y audio AAC (los que abre cualquier
    # reproductor y las redes sociales). logger=None oculta la barra de progreso.
    video.write_videofile(video_path, fps=24, codec="libx264", audio_codec="aac", logger=None)
    # Cerrar los clips libera los archivos (en Windows, un archivo abierto no se puede borrar).
    audio.close()
    video.close()
    return video_path


def main():
    print("Estudio de contenido de Rodados Sur")
    # Marta escribe el tema, por ejemplo "service completo de primavera".
    topic = input("¿Sobre qué es la promo?: ").strip()
    if not topic:
        print("Error controlado: el tema no puede estar vacío.")
        return
    try:
        script = write_promo_script(topic)
    # Los mismos errores controlados de siempre: JSON inválido, sin conexión o sin clave.
    except (ValueError, ConnectionError, MissingAPIKeyError) as error:
        print(f"Error controlado: {error}")
        return
    folder = create_promo_folder()
    save_json(script, os.path.join(folder, "guion.json"))
    # json.dumps (con s) devuelve el JSON como texto, para mostrarlo en la terminal.
    print(json.dumps(script, ensure_ascii=False, indent=2))
    print(f"Guion guardado en {folder}")

    # Primero se intenta por API; si no hay claves o falla, se sigue con la imagen de la web.
    image_path = None
    try:
        image_path = generate_image(script["descripcion_visual"], os.path.join(folder, "imagen_ia.jpg"))
    except (ConnectionError, ValueError) as error:
        print(f"Error controlado: {error}")
    if image_path:
        print(f"Imagen generada por API: {image_path}")
    else:
        print("\nLa imagen: copia la descripcion_visual y genérala en ChatGPT, Gemini o Copilot.")
        print("Guárdala en esta carpeta con el nombre imagen (png, jpg o webp).")
        input("Presiona Enter cuando esté (sin imagen, Rayo arma una placa con el título): ")
        image_path = take_web_image(folder)
    poster_file = os.path.join(folder, "afiche.png")
    try:
        poster_path = make_poster(script, image_path, poster_file)
    # Si el archivo no es una imagen (por ejemplo, se descargó una página web), Pillow da
    # un OSError: lo avisamos y armamos la placa, así el video sale igual.
    except OSError as error:
        print(f"Error controlado: no pude abrir la imagen ({error}). Uso la placa.")
        poster_path = make_poster(script, None, poster_file)
    print(f"Afiche guardado en {poster_path}")

    try:
        # La narración con la voz de Google (Clase 6). Si falla internet, save_audio da ConnectionError.
        audio_path = save_audio(script["narracion"], os.path.join(folder, "narracion.mp3"))
    except ConnectionError as error:
        print(f"Error controlado: {error}")
        return
    print(f"Narración guardada en {audio_path}")
    # Armar el video tarda unos segundos: el mensaje avisa que el programa sigue trabajando.
    print("Armando el video...")
    video_path = make_video(poster_path, audio_path, os.path.join(folder, "promo.mp4"))
    print(f"Video listo: {video_path}")


if __name__ == "__main__":
    main()
