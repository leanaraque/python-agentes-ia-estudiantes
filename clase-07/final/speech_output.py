# speech_output.py: la SALIDA por voz de Rayo (texto a voz, TTS).
# Dos librerías, dos enfoques:
# - pyttsx3 usa las voces que ya trae Windows: funciona sin internet, suena más "robótica".
# - gTTS le manda el texto a Google y recibe un mp3: suena más natural, pero necesita internet.
import pyttsx3
from gtts import gTTS, gTTSError

# Velocidad de lectura en palabras por minuto. pyttsx3 arranca en 200: un poco rápido.
SPEECH_RATE = 170


def choose_spanish_voice(engine):
    """Elige la primera voz en español instalada en el sistema. Devuelve su nombre, o None si no hay."""
    # Cada voz trae sus idiomas, por ejemplo ['es-MX'] o ['en-US'].
    for voice in engine.getProperty("voices"):
        # Si la lista no está vacía y el primer idioma empieza con "es", es una voz en español.
        if voice.languages and voice.languages[0].startswith("es"):
            engine.setProperty("voice", voice.id)
            return voice.name
    # Sin voces en español, queda la voz por defecto (en inglés suele leer el español muy mal).
    return None


def speak(text):
    """Lee el texto en voz alta con una voz instalada en la computadora (no necesita internet)."""
    try:
        # Creamos el motor cada vez: reusar uno viejo puede dejar mudas las respuestas siguientes.
        engine = pyttsx3.init()
        choose_spanish_voice(engine)
        engine.setProperty("rate", SPEECH_RATE)
        # say() pone el texto en la cola; runAndWait() lo lee y espera a que termine.
        engine.say(text)
        engine.runAndWait()
    # La voz es un extra: si falla por cualquier motivo, se avisa y la conversación sigue por texto.
    except Exception as error:
        print(f"   [voz] No pude reproducir el audio: {error}")


def save_audio(text, path):
    """Convierte el texto en un archivo mp3 con la voz de Google (necesita internet)."""
    try:
        # lang="es": español. save() descarga el audio y lo guarda en el archivo.
        gTTS(text=text, lang="es").save(path)
    # gTTSError: Google no respondió (sin internet, demasiados pedidos...).
    # Lo convertimos en ConnectionError, el mismo error que usamos con requests.
    except gTTSError as exc:
        raise ConnectionError(f"no pude generar el audio ({exc}).") from exc
    return path


# Prueba: solo corre con "python speech_output.py".
if __name__ == "__main__":
    # Lista las voces de Windows: la calidad de pyttsx3 depende de cuáles haya.
    print("Voces instaladas:")
    for voice in pyttsx3.init().getProperty("voices"):
        print(f"- {voice.name} {voice.languages}")
    # Rayo habla por los parlantes.
    speak("Hola, soy Rayo, el asistente de Rodados Sur.")
    # Y genera un audio de una clienta: lo vamos a usar para probar la voz a texto sin micrófono.
    path = save_audio("Hola, soy Ana. ¿Cómo va mi bici? Es la orden 1043.", "consulta.mp3")
    print(f"Audio guardado en {path}.")
