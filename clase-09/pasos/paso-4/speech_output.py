import pyttsx3
from gtts import gTTS, gTTSError

SPEECH_RATE = 170


def choose_spanish_voice(engine):
    """Elige la primera voz en español instalada en el sistema. Devuelve su nombre, o None si no hay."""
    for voice in engine.getProperty("voices"):
        if voice.languages and voice.languages[0].startswith("es"):
            engine.setProperty("voice", voice.id)
            return voice.name
    return None


def speak(text):
    """Lee el texto en voz alta con una voz instalada en la computadora (no necesita internet)."""
    try:
        engine = pyttsx3.init()
        choose_spanish_voice(engine)
        engine.setProperty("rate", SPEECH_RATE)
        engine.say(text)
        engine.runAndWait()
    except Exception as error:
        print(f"   [voz] No pude reproducir el audio: {error}")


def save_audio(text, path):
    """Convierte el texto en un archivo mp3 con la voz de Google (necesita internet)."""
    try:
        gTTS(text=text, lang="es").save(path)
    except gTTSError as exc:
        raise ConnectionError(f"no pude generar el audio ({exc}).") from exc
    return path


if __name__ == "__main__":
    print("Voces instaladas:")
    for voice in pyttsx3.init().getProperty("voices"):
        print(f"- {voice.name} {voice.languages}")
    speak("Hola, soy Rayo, el asistente de Rodados Sur.")
    path = save_audio("Hola, soy Ana. ¿Cómo va mi bici? Es la orden 1043.", "consulta.mp3")
    print(f"Audio guardado en {path}.")
