import os

import requests
import speech_recognition as sr
from dotenv import load_dotenv

from llm_client import MissingAPIKeyError

load_dotenv()

STT_URL = "https://api.groq.com/openai/v1/audio/transcriptions"
STT_MODEL = "whisper-large-v3-turbo"
STT_CONTEXT = "Rodados Sur, tienda y taller de bicicletas."


def transcribe_audio(audio_bytes, filename):
    """Envía un audio a Whisper (en Groq) y devuelve el texto que reconoció."""
    api_key = os.getenv("GROQ_API_KEY")
    if not api_key:
        raise MissingAPIKeyError("falta GROQ_API_KEY en el archivo .env.")
    headers = {"Authorization": f"Bearer {api_key}"}
    files = {"file": (filename, audio_bytes)}
    data = {"model": STT_MODEL, "language": "es", "prompt": STT_CONTEXT}
    try:
        response = requests.post(STT_URL, headers=headers, files=files, data=data, timeout=60)
        response.raise_for_status()
    except requests.exceptions.RequestException as exc:
        raise ConnectionError(f"no pude transcribir el audio ({exc}).") from exc

    try:
        text = response.json()["text"].strip()
    except (ValueError, KeyError) as exc:
        raise ValueError("el servicio de voz devolvió una respuesta con un formato inesperado.") from exc
    if not text:
        raise ValueError("no se entendió nada en el audio.")
    return text


def transcribe_file(path):
    """Transcribe un archivo de audio (mp3, wav, m4a...) y devuelve el texto."""
    with open(path, "rb") as file:
        return transcribe_audio(file.read(), os.path.basename(path))


def listen_and_transcribe():
    """Escucha una frase por el micrófono y devuelve el texto que reconoció Whisper."""
    recognizer = sr.Recognizer()
    try:
        with sr.Microphone() as source:
            recognizer.adjust_for_ambient_noise(source, duration=0.5)
            print("   [micrófono] Te escucho...")
            audio = recognizer.listen(source, timeout=5, phrase_time_limit=15)
    except sr.WaitTimeoutError as exc:
        raise ValueError("no escuché nada. Habla apenas aparezca 'Te escucho'.") from exc
    except (AttributeError, OSError) as exc:
        raise RuntimeError("no encontré un micrófono disponible (o falta instalar PyAudio).") from exc
    print("   [micrófono] Transcribiendo...")
    return transcribe_audio(audio.get_wav_data(), "voz.wav")


if __name__ == "__main__":
    try:
        print("Archivo:", transcribe_file("consulta.mp3"))
    except (FileNotFoundError, ValueError, ConnectionError, MissingAPIKeyError) as error:
        print(f"Error controlado: {error}")
    try:
        print("Micrófono:", listen_and_transcribe())
    except (RuntimeError, ValueError, ConnectionError, MissingAPIKeyError) as error:
        print(f"Error controlado: {error}")
