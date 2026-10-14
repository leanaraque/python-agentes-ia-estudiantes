# speech_input.py: la ENTRADA por voz de Rayo (voz a texto, STT o ASR).
# Usamos Whisper, el modelo de reconocimiento de voz de OpenAI, a través de Groq:
# la misma cuenta y la misma GROQ_API_KEY que el modelo de lenguaje.
import os

import requests
# SpeechRecognition se importa con otro nombre: speech_recognition. "as sr" lo acorta.
import speech_recognition as sr
from dotenv import load_dotenv

# Reusamos el error de la Clase 3: si falta la clave, el mensaje es el mismo.
from llm_client import MissingAPIKeyError

load_dotenv()

# Otra dirección de Groq: la de transcripciones de audio (no la de chat).
STT_URL = "https://api.groq.com/openai/v1/audio/transcriptions"
# whisper-large-v3-turbo: rápido y gratuito en Groq. También existe whisper-large-v3 (más lento).
STT_MODEL = "whisper-large-v3-turbo"
# Contexto para Whisper, como un prompt chiquito: le ayuda a escribir bien los nombres propios.
# Sin él, en la prueba escribió "Rodado Sur".
STT_CONTEXT = "Rodados Sur, tienda y taller de bicicletas."


def transcribe_audio(audio_bytes, filename):
    """Envía un audio a Whisper (en Groq) y devuelve el texto que reconoció."""
    api_key = os.getenv("GROQ_API_KEY")
    if not api_key:
        raise MissingAPIKeyError("falta GROQ_API_KEY en el archivo .env.")
    # Sin "Content-Type": requests lo arma solo cuando mandamos un archivo.
    headers = {"Authorization": f"Bearer {api_key}"}
    # Un audio no viaja como JSON: viaja como ARCHIVO (files=), con un nombre que indica el formato.
    files = {"file": (filename, audio_bytes)}
    # Los demás datos van como campos de formulario (data=), no como JSON.
    data = {"model": STT_MODEL, "language": "es", "prompt": STT_CONTEXT}
    try:
        response = requests.post(STT_URL, headers=headers, files=files, data=data, timeout=60)
        response.raise_for_status()
    except requests.exceptions.RequestException as exc:
        raise ConnectionError(f"no pude transcribir el audio ({exc}).") from exc

    try:
        # La respuesta es un JSON chiquito: {"text": " Hola, soy Ana..."}.
        # strip() saca el espacio que Whisper suele dejar al principio.
        text = response.json()["text"].strip()
    except (ValueError, KeyError) as exc:
        raise ValueError("el servicio de voz devolvió una respuesta con un formato inesperado.") from exc
    if not text:
        raise ValueError("no se entendió nada en el audio.")
    return text


def transcribe_file(path):
    """Transcribe un archivo de audio (mp3, wav, m4a...) y devuelve el texto."""
    # "rb": leer en modo binario. Un audio son bytes, no texto.
    with open(path, "rb") as file:
        # os.path.basename deja solo el nombre del archivo (sin carpetas): "consulta.mp3".
        return transcribe_audio(file.read(), os.path.basename(path))


def listen_and_transcribe():
    """Escucha una frase por el micrófono y devuelve el texto que reconoció Whisper."""
    recognizer = sr.Recognizer()
    try:
        # sr.Microphone() abre el micrófono por defecto de Windows (usa PyAudio por dentro).
        # El "with" lo cierra al terminar, aunque haya un error.
        with sr.Microphone() as source:
            # Escucha medio segundo el "silencio" de la sala para saber cuánto ruido hay.
            recognizer.adjust_for_ambient_noise(source, duration=0.5)
            print("   [micrófono] Te escucho...")
            # listen() espera a que empieces a hablar y corta cuando te callas.
            # timeout=5: si en 5 segundos no empezaste, se rinde (WaitTimeoutError).
            # phrase_time_limit=15: una frase de 15 segundos como máximo.
            audio = recognizer.listen(source, timeout=5, phrase_time_limit=15)
    # Los tres casos de la Etapa 3, convertidos en errores que assistant.py ya sabe manejar:
    # 1. No se detectó audio.
    except sr.WaitTimeoutError as exc:
        raise ValueError("no escuché nada. Habla apenas aparezca 'Te escucho'.") from exc
    # 2. El micrófono no está disponible: sin PyAudio, SpeechRecognition da AttributeError;
    #    sin micrófono conectado (o sin permiso de Windows), OSError.
    except (AttributeError, OSError) as exc:
        raise RuntimeError("no encontré un micrófono disponible (o falta instalar PyAudio).") from exc
    print("   [micrófono] Transcribiendo...")
    # 3. Si el reconocimiento falla, transcribe_audio ya lanza ConnectionError o ValueError.
    # get_wav_data() convierte lo grabado en un archivo WAV (bytes): el mismo camino que un archivo.
    return transcribe_audio(audio.get_wav_data(), "voz.wav")


# Prueba: primero el archivo (funciona sin micrófono) y después el micrófono.
if __name__ == "__main__":
    try:
        print("Archivo:", transcribe_file("consulta.mp3"))
    except (FileNotFoundError, ValueError, ConnectionError, MissingAPIKeyError) as error:
        print(f"Error controlado: {error}")
    # Un try aparte: si el micrófono falla, la prueba del archivo ya se mostró.
    try:
        print("Micrófono:", listen_and_transcribe())
    except (RuntimeError, ValueError, ConnectionError, MissingAPIKeyError) as error:
        print(f"Error controlado: {error}")
