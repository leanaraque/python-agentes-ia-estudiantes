# Clase 7 · Rayo crea contenido

Hoy Rayo arma una **promo de Rodados Sur** de punta a punta: el guion (texto), la imagen, el afiche, la narración (audio) y un video MP4. Es un programa para Marta, aparte del agente: ella elige el tema y Rayo propone la promo. El agente de las clases anteriores no cambia.

## Qué vimos

- **IA generativa multimedia:** texto (LLM), imagen (difusión), audio (TTS) y video (difusión temporal). Se pueden combinar: una imagen a partir de un texto, un video con voz.
- **Difusión:** el modelo parte de ruido puro y lo va limpiando paso a paso, guiado por el texto.
- **Una app creativa por dentro:** entrada, interpretación (el guion en JSON), motor generativo, procesador de salida e historial (una carpeta por promo).
- **La IA crea, Python compone:** la imagen no lleva texto; el título, el slogan y la dirección los escribe Python con **Pillow**, exactos.
- **MoviePy** une el afiche y la narración en un video. FFmpeg viene con pip: no hay que instalar nada más.
- **Una regla contra los inventos:** sin "no inventes precios, descuentos...", 1 de 8 promos inventó un descuento; con la regla, 0 de 14.
- **Ética:** autoría (marcar lo generado con IA), datos de entrenamiento, sesgos, deepfakes y licencias. La que publica es una persona.

## Archivos

| Carpeta | Contenido |
|---|---|
| [`inicio/`](./inicio) | El proyecto como terminó la Clase 6 |
| [`pasos/`](./pasos) | El proyecto completo en cada paso de la clase (`paso-1` a `paso-4`; el 4 es opcional) |
| [`final/`](./final) | El proyecto terminado, **comentado línea por línea** |
| [`requirements.txt`](./requirements.txt) | Las librerías de esta clase, para descargar |

Archivo nuevo de esta clase: `content_studio.py`. Cambian `requirements.txt` (con Pillow y MoviePy) y, en el paso 4, `.env.example`.

## Armar la carpeta de la clase

Desde la carpeta del curso (la que contiene a `clase-06`):

```powershell
New-Item -ItemType Directory clase-07
Copy-Item clase-06\*.py, clase-06\ordenes.json, clase-06\.env, clase-06\.env.example, clase-06\.gitignore clase-07
```

`requirements.txt` no se copia: hoy se descarga el nuevo. En VS Code: **File > Open Folder** > `clase-07`. En una terminal nueva:

```powershell
python -m venv .venv
.venv\Scripts\Activate.ps1
Invoke-WebRequest https://raw.githubusercontent.com/leanaraque/python-agentes-ia-estudiantes/main/clase-07/requirements.txt -OutFile requirements.txt -UseBasicParsing
python -m pip install -r requirements.txt
```

(Si la descarga falla: abre [`requirements.txt`](./requirements.txt), botón **Download raw file**, y guárdalo en `clase-07`.)

Para comprobar que todo está bien:

```powershell
python -c "import sys, os, dotenv, gtts, PIL, moviepy; dotenv.load_dotenv(); print(sys.prefix); print('Clave de Groq cargada:', bool(os.getenv('GROQ_API_KEY'))); print('Pillow', PIL.__version__); print('Entorno listo')"
```

Tiene que mostrar la ruta de la caja (termina en `clase-07\.venv`), `Clave de Groq cargada: True`, `Pillow 11.3.0` y `Entorno listo`.

Por último: **Ctrl + Shift + P** > `Python: Select Interpreter` > **('.venv': venv)**. El `.env` no cambia (salvo el paso 4, opcional).

**¿No tienes la carpeta de la Clase 6?** Copia el contenido de [`inicio/`](./inicio) en una carpeta `clase-06` y crea su `.env` a partir de `.env.example` (una variable por línea, con tu clave de Groq).

## Cómo probarlo

1. Crea `content_studio.py` y pega el código del paso que corresponda:

   ```powershell
   New-Item content_studio.py; code content_studio.py
   ```

2. Ejecútalo y escribe el tema de la promo (por ejemplo, `service completo de primavera`):

   ```powershell
   python content_studio.py
   ```

3. Desde el paso 2, el programa pide **dos** cosas: el tema y, después del guion, un **Enter** en la línea `Presiona Enter cuando esté (sin imagen, Rayo arma una placa con el título):`. El afiche se arma recién con ese segundo Enter. Lo más simple es tener la imagen en la carpeta **antes** de ejecutar: copia una `descripcion_visual` (está en `guion.json`, dentro de `promos`), genera la imagen en ChatGPT, Gemini o Copilot, descárgala y muévela de Descargas a `clase-07` con el nombre `imagen.png`:

   ```powershell
   Get-ChildItem "$HOME\Downloads\*" -Include *.png, *.jpg, *.jpeg, *.webp | Sort-Object LastWriteTime | Select-Object -Last 1 | Move-Item -Destination imagen.png
   ```

   Después ejecuta `python content_studio.py`, escribe el tema y presiona **Enter** en la segunda pregunta. Sin imagen, Rayo arma una placa con el título.

4. Abre la carpeta de la última promo (guion, imagen, afiche y, desde el paso 3, narración y video):

   ```powershell
   Invoke-Item (Get-ChildItem promos | Sort-Object Name | Select-Object -Last 1).FullName
   ```

### Paso 4 (opcional): la imagen por API

Con una cuenta gratuita de Cloudflare, la imagen se genera sola con FLUX:

1. En `dash.cloudflare.com`, crea una cuenta. En el menú, **Workers AI** > **Use REST API**: copia el **Account ID** y presiona **Create a Workers AI API Token** > **Create API Token** > **Copy API Token**.
2. Agrega al final de tu `.env` (una por línea, sin comillas):

   ```text
   CLOUDFLARE_ACCOUNT_ID=tu_numero_de_cuenta
   CLOUDFLARE_API_TOKEN=tu_token
   ```

3. Usa el `content_studio.py` de [`pasos/paso-4`](./pasos/paso-4). Sin esas variables, funciona igual que el paso 3.

El plan gratuito trae una cuota diaria (10.000 "neuronas", que alcanzan para más de 100 imágenes). El token es una clave: nunca lo subas a GitHub.

### Problemas frecuentes

| Síntoma | Solución |
|---|---|
| `ERROR: Could not open requirements file` | Falta descargar el `requirements.txt` de hoy (ver "Armar la carpeta") |
| `ModuleNotFoundError: No module named 'PIL'` (o `'moviepy'`) | La caja no está activa o se instaló otro `requirements.txt`. Activa la caja, descarga el de hoy y repite `python -m pip install -r requirements.txt`: tiene que decir `Successfully installed` con 24 librerías (25 con Python 3.13) |
| `imagen.png` sigue en `clase-07` y la carpeta de la promo solo tiene `guion.json` | Faltó el segundo Enter: el programa quedó esperando en "Presiona Enter cuando esté" (o se cerró antes). Ejecútalo de nuevo, escribe el tema y presiona Enter en esa línea |
| El comando de mover la imagen no hace nada | No hay imágenes en Descargas: el navegador la guardó en otro lado. Arrástrala desde el Explorador de Windows a `clase-07` y renómbrala `imagen` |
| `Cannot create a file when that file already exists` | Ya hay un `imagen.png` sin usar: bórralo o ejecuta el programa para que lo use |
| `Error controlado: no pude abrir la imagen (...). Uso la placa.` | Lo descargado no era una imagen: vuelve a descargarla |
| `Error controlado: no pude generar el audio (...)` | gTTS necesita internet: revisa la conexión y repite |
| `Error controlado: no pude generar la imagen (401 Client Error ...)` | Paso 4: el número de cuenta o el token de Cloudflare están mal. Revísalos en el `.env` |
| `429 Client Error: Too Many Requests` | Superaste el límite gratuito por minuto de Groq. Espera un minuto y repite |

## Antes de publicar algo generado con IA

1. ¿Los datos son los del negocio (precios, fechas, ofertas)?
2. ¿La imagen tiene estereotipos o rostros reales sin permiso?
3. ¿Dice que es generada con IA?
4. ¿La licencia del servicio permite el uso comercial?

Si alguna falla, se corrige y se vuelve a revisar. Voces y rostros reales: nunca sin permiso.

## Tarea (1 hora como máximo)

1. **Dos promos de Rodados Sur:** "alquiler de bicis para el fin de semana" y una a elección. Revisa cada una con las cuatro preguntas de arriba y anota qué corregirías antes de publicar.
2. **El afiche con tu marca:** en `content_studio.py`, cambia `BRAND_COLOR` y `ACCENT_COLOR` (colores en hexadecimal, por ejemplo `#1B5E20`).
3. **Opcional:** el paso 4, con una cuenta de Cloudflare.
4. Leer en la plataforma "Estrategias integradas, nube y servicios empresariales" (Módulo 5).
