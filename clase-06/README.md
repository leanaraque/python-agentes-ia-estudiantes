# Clase 6 · Rayo escucha y habla

Hoy el agente de **Rodados Sur** suma la voz: **habla** (texto a voz) y **escucha** (voz a texto), sin cambiar su arquitectura. El agente de la Clase 5 queda igual: la voz entra y sale por los bordes.

## Qué vimos

- **IA conversacional con voz:** captura del micrófono → voz a texto (ASR) → el agente → texto a voz (TTS) → parlante.
- **Texto a voz:** concatenativo (fragmentos pregrabados) o neuronal (una red genera la voz).
  - **pyttsx3** usa las voces de Windows, sin internet.
  - **gTTS** usa la voz de Google, en la nube, y genera un mp3.
- **Voz a texto:** **Whisper** es una sola red neuronal, del sonido al texto. Lo usamos en Groq, con la misma clave. Un audio viaja como **archivo** (`files=`), no como JSON.
- **SpeechRecognition** escucha el micrófono: mide el ruido, espera a que hables y corta cuando te callas.
- **Los tres errores de la Etapa 3:** no se detecta audio, no hay micrófono, falla el reconocimiento. Los tres se convierten en errores controlados.
- **La voz cambia el prompt:** sin reglas, una voz leyó "asterisco asterisco" y "45.000 dólares".
- **Whisper también alucina:** con silencio escribió "Gracias por ver el video.".

## Archivos

| Carpeta | Contenido |
|---|---|
| [`inicio/`](./inicio) | El proyecto como terminó la Clase 5 |
| [`pasos/`](./pasos) | El proyecto completo en cada paso de la clase (`paso-1` a `paso-4`) |
| [`final/`](./final) | El proyecto terminado, **comentado línea por línea** |
| [`requirements.txt`](./requirements.txt) | Las librerías de esta clase, para descargar y reemplazar el de la Clase 5 |

Archivos nuevos de esta clase: `speech_output.py` y `speech_input.py`. Cambian `assistant.py` y `requirements.txt` (con las librerías de voz).

La tarea de la Clase 5 resuelta está en [`../clase-05/tarea-resuelta/tools.py`](../clase-05/tarea-resuelta/tools.py).

## Armar la carpeta de la clase

Desde la carpeta del curso (la que contiene a `clase-05`):

```powershell
New-Item -ItemType Directory clase-06
Copy-Item clase-05\*.py, clase-05\ordenes.json, clase-05\requirements.txt, clase-05\.env, clase-05\.env.example, clase-05\.gitignore clase-06
```

En VS Code: **File > Open Folder** > `clase-06`. El `requirements.txt` que copiaste es el de la Clase 5: hay que reemplazarlo por el de hoy, [`requirements.txt`](./requirements.txt), que trae las librerías de voz. En una terminal nueva, este comando lo descarga y reemplaza al viejo:

```powershell
Invoke-WebRequest https://raw.githubusercontent.com/leanaraque/python-agentes-ia-estudiantes/main/clase-06/requirements.txt -OutFile requirements.txt -UseBasicParsing
```

(O, a mano: abre [`requirements.txt`](./requirements.txt), botón **Download raw file**, y guárdalo en `clase-06` reemplazando el viejo.)

Después:

```powershell
python -m venv .venv
.venv\Scripts\Activate.ps1
python -m pip install -r requirements.txt
```

Por último: **Ctrl + Shift + P** > `Python: Select Interpreter` > **('.venv': venv)**. El `.env` no cambia: Whisper usa la misma `GROQ_API_KEY`.

**¿No tienes la carpeta de la Clase 5?** Copia el contenido de [`inicio/`](./inicio) en una carpeta `clase-05` y crea su `.env` a partir de `.env.example` (una variable por línea, con tu clave de Groq).

## Cómo probarlo

1. Rayo habla y genera un audio de prueba (`consulta.mp3`):

   ```powershell
   python speech_output.py
   ```

2. Whisper transcribe ese audio (y, desde el paso 3, también escucha el micrófono):

   ```powershell
   python speech_input.py
   ```

3. El agente completo:

   ```powershell
   python assistant.py
   ```

   Escribe `voz`, presiona **Enter** antes de cada consulta y habla cuando aparece "Te escucho...". Por ejemplo: "Hola, soy Ana. ¿Cómo va mi bici? Es la orden mil cuarenta y tres." Si escribes algo en lugar de presionar Enter, Rayo usa lo escrito (y responde hablando).

### Problemas frecuentes

| Síntoma | Solución |
|---|---|
| `ModuleNotFoundError: No module named 'gtts'` | Se instaló el `requirements.txt` de la Clase 5. Descarga el de hoy con el comando `Invoke-WebRequest` de "Armar la carpeta" (o reemplaza su contenido por el de [`requirements.txt`](./requirements.txt) y guarda con **Ctrl + S**) y repite `python -m pip install -r requirements.txt`. Tiene que decir `Successfully installed` con 16 librerías |
| No se escucha a Rayo | Revisa el volumen y la salida de audio de Windows |
| Rayo habla con acento inglés | Tu Windows no tiene voces en español: `python speech_output.py` muestra las voces instaladas |
| `pip install` falla en PyAudio | Con Python 3.14 se saltea solo (todavía no tiene instalador). Sin PyAudio todo funciona menos el micrófono: en modo voz, escribe |
| `no encontré un micrófono disponible (o falta instalar PyAudio)` | No hay micrófono o falta PyAudio. Puedes escribir en modo voz, o grabar con la app **Grabadora de sonido**, copiar la grabación como `mi_consulta.m4a` y transcribirla con `python -c "from speech_input import transcribe_file; print(transcribe_file('mi_consulta.m4a'))"` |
| Siempre `no escuché nada`, aunque hables | Configuración > Privacidad y seguridad > Micrófono > activa **Permitir que las aplicaciones de escritorio accedan al micrófono**, y revisa el micrófono predeterminado en Configuración > Sistema > Sonido |
| Transcribe frases que nadie dijo | Ruido de fondo: Whisper alucina con ruido. Acércate al micrófono |
| `Error controlado: [Errno 2] No such file or directory: 'consulta.mp3'` | Primero corre `python speech_output.py`, que genera ese audio |
| `429 Client Error: Too Many Requests` | Superaste el límite gratuito por minuto. Espera un minuto y sigue: la conversación no se pierde |

## Tarea (1 hora como máximo)

1. **Hablar con Rayo** con 5 consultas reales (o, sin micrófono, escribiendo en modo voz). Anotar qué entendió mal Whisper y por qué crees que pasó.
2. **Elegir la velocidad de la voz:** en `speech_output.py`, probar `SPEECH_RATE` en 130, 170 y 220 y quedarse con la que mejor se entienda.
3. Leer en la plataforma "Generación de contenido multimedia" (Módulo 4).
