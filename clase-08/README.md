# Clase 8 · Del script al servicio

Hoy Rayo hace dos cosas nuevas para Rodados Sur: procesa **las consultas del día** todas juntas, en un pipeline, y sale **a la web** con Streamlit. Primero funciona en tu computadora; después, publicado en internet.

## Qué vimos

- **Estrategia integrada:** la IA no es una herramienta suelta. Es una pieza del negocio, conectada a sus datos (el FAQ, las órdenes) y a servicios en la nube por APIs (Groq, Open-Meteo, Google, Cloudflare).
- **La nube:** elasticidad, disponibilidad, integración y actualización. Medido: el pipeline tarda 5 segundos con Groq y 70 con un modelo local chico.
- **Un pipeline:** entrada, validación, modelo, decisión, entrega y registro. La validación (Python) frena lo que no sirve antes de gastar una llamada. **Lo que falla se marca y la línea sigue.**
- **Registro:** `logging` (fecha, hora y nivel, en la terminal y en `pipeline.log`), tiempos con `time.perf_counter` y metadatos en JSON.
- **Streamlit:** un programa de Python que se ve como página web. Se ejecuta de arriba a abajo en cada clic. `app.py` solo se ocupa de la pantalla: la lógica sigue en los otros archivos.
- **Publicar:** el código va a GitHub (sin el `.env`), Streamlit Community Cloud lo ejecuta en Linux y la clave va en **Secrets**, no en el código.

## Archivos

| Carpeta | Contenido |
|---|---|
| [`inicio/`](./inicio) | El proyecto como terminó la Clase 7 |
| [`pasos/`](./pasos) | El proyecto completo en cada paso de la clase (`paso-1` a `paso-4`) |
| [`final/`](./final) | El proyecto terminado, con `pipeline.py` y `app.py` **comentados línea por línea** |
| [`requirements.txt`](./requirements.txt) | Las librerías de esta clase, para descargar |
| [`consultas_del_dia.json`](./consultas_del_dia.json) | Las 9 consultas del día, para descargar |

Archivos nuevos de esta clase: `consultas_del_dia.json`, `pipeline.py` y `app.py`. Cambia `requirements.txt` (con Streamlit). El agente no cambia.

## Armar la carpeta de la clase

Desde la carpeta del curso (la que contiene a `clase-07`):

```powershell
New-Item -ItemType Directory clase-08
Copy-Item clase-07\*.py, clase-07\ordenes.json, clase-07\.env, clase-07\.env.example, clase-07\.gitignore clase-08
```

`requirements.txt` no se copia: hoy se descarga el nuevo. En VS Code: **File > Open Folder** > `clase-08`. En una terminal nueva:

```powershell
python -m venv .venv
.venv\Scripts\Activate.ps1
Invoke-WebRequest https://raw.githubusercontent.com/leanaraque/python-agentes-ia-estudiantes/main/clase-08/requirements.txt -OutFile requirements.txt -UseBasicParsing
python -m pip install -r requirements.txt
```

(Si la descarga falla: abre [`requirements.txt`](./requirements.txt), botón **Download raw file**, y guárdalo en `clase-08`.)

Para comprobar que todo está bien:

```powershell
python -c "import sys, os, dotenv, streamlit; dotenv.load_dotenv(); print(sys.prefix); print('Clave de Groq cargada:', bool(os.getenv('GROQ_API_KEY'))); print('Streamlit', streamlit.__version__); print('Entorno listo')"
```

Tiene que mostrar la ruta de la caja (termina en `clase-08\.venv`), `Clave de Groq cargada: True`, `Streamlit 1.50.0` y `Entorno listo`.

Por último: **Ctrl + Shift + P** > `Python: Select Interpreter` > **('.venv': venv)**. El `.env` no cambia.

**¿No tienes la carpeta de la Clase 7?** Copia el contenido de [`inicio/`](./inicio) en una carpeta `clase-07` y crea su `.env` a partir de `.env.example` (una variable por línea, con tu clave de Groq).

## Cómo probarlo

### El pipeline (pasos 1 y 2)

1. Descarga las consultas del día y crea `pipeline.py` con el código del paso que corresponda:

   ```powershell
   Invoke-WebRequest https://raw.githubusercontent.com/leanaraque/python-agentes-ia-estudiantes/main/clase-08/consultas_del_dia.json -OutFile consultas_del_dia.json -UseBasicParsing
   New-Item pipeline.py; code pipeline.py
   ```

2. Ejecútalo. **No pide nada**: procesa las 9 consultas y termina solo (unos 5 segundos):

   ```powershell
   python pipeline.py
   ```

   Tiene que mostrar 4 listas, 3 para Marta y 2 inválidas (las respuestas cambian un poco en cada ejecución). Desde el paso 2, también deja `pipeline.log` y una carpeta en `reportes` con `resultados.json` y `metadatos.json`.

3. **Como máximo, dos ejecuciones por minuto.** Cada una gasta unos 3.300 tokens y el plan gratuito de Groq permite 8.000 por minuto. A la tercera aparecen errores `429`: el pipeline no se cae, marca esas consultas "con error". Espera un minuto y vuelve a andar.

### La web (pasos 3 y 4)

1. Crea `app.py` con el código del paso que corresponda:

   ```powershell
   New-Item app.py; code app.py
   ```

2. Ejecútalo con Streamlit (**no** con `python app.py`):

   ```powershell
   python -m streamlit run app.py
   ```

   - **La primera vez**, la terminal pide un `Email:`: presiona **Enter** sin escribir nada.
   - Se abre el navegador en `http://localhost:8501`. La terminal queda ocupada: no está trabada, está sirviendo la página.
   - Para detenerla: **Ctrl + C** en la terminal (si no responde, cierra la terminal con el ícono de la papelera).

3. Pregunta, por ejemplo: "¿Ya está lista la orden 1042? ¿Y cuánto sale el service completo?". En el paso 4, la pestaña **Consultas del día** procesa el archivo con el pipeline.

## Publicar tu Rayo en internet (opcional)

Necesitas una cuenta de [GitHub](https://github.com) (gratis). Unos 15 minutos.

1. **La carpeta `publicar`**, con solo lo que va a la nube. Dentro de `clase-08`, con el paso 4 terminado:

   ```powershell
   New-Item -ItemType Directory publicar; Copy-Item app.py, pipeline.py, assistant.py, llm_client.py, tools.py, weather.py, speech_input.py, speech_output.py, ordenes.json, consultas_del_dia.json, requirements.txt publicar
   Invoke-Item publicar
   ```

   Tiene que tener 11 archivos. **Nunca** el `.env`.

2. **El repositorio.** En [github.com/new](https://github.com/new): un nombre (por ejemplo `rodados-sur`), **Public**, marca **Add a README file** y presiona **Create repository**. Después, **Add file** > **Upload files**, arrastra los 11 archivos de la carpeta `publicar` y presiona **Commit changes**.

3. **La cuenta de Streamlit.** En [share.streamlit.io](https://share.streamlit.io): **Continue to sign-in** > **Continue with GitHub** y autoriza. Completa el formulario y presiona **Continue**.

4. **La app.** **Create app** > **Yup, I have an app**. Elige tu repositorio, la rama `main` y el archivo `app.py`. En **App URL** pon un nombre fácil. En **Advanced settings** deja Python 3.12 y en **Secrets** pega esto, con tu clave y tu nombre de asistente (formato TOML: espacios alrededor del `=` y el valor entre comillas):

   ```toml
   GROQ_API_KEY = "tu_clave_de_groq"
   ASSISTANT_NAME = "Rayo"
   WEATHER_LATITUDE = "-34.61"
   WEATHER_LONGITUDE = "-58.38"
   ```

   Presiona **Save** y **Deploy**. Espera unos minutos y comparte el link.

**Ojo:** la app es pública y usa tu clave. El plan gratuito de Groq no cobra, pero cualquiera con el link gasta tu límite. Para cerrarla: en `share.streamlit.io`, los tres puntos de la app > **Delete**.

## Problemas frecuentes

| Síntoma | Solución |
|---|---|
| `ERROR: Could not open requirements file` | Falta descargar el `requirements.txt` de hoy (ver "Armar la carpeta") |
| `ModuleNotFoundError: No module named 'streamlit'` | La caja no está activa o se instaló otro `requirements.txt`. Activa la caja, descarga el de hoy y repite `python -m pip install -r requirements.txt` |
| `Error controlado: [Errno 2] No such file or directory: 'consultas_del_dia.json'` | Falta descargar el archivo de consultas (ver "El pipeline") |
| `error - no pude hablar con el modelo (429 Client Error: Too Many Requests ...)` | Superaste el límite por minuto de Groq. Espera un minuto y repite |
| La terminal pide `Email:` y no pasa nada | Es Streamlit, la primera vez: presiona Enter |
| La terminal muestra `http://localhost:8502` | Hay otra app de Streamlit abierta en otra terminal: usa la dirección que muestra, o cierra la otra |
| `missing ScriptRunContext` | Se ejecuta con `python -m streamlit run app.py`, no con `python app.py` |
| En la app publicada: `Error controlado: falta GROQ_API_KEY ...` | Faltan los Secrets o están mal escritos: **Manage app** > los tres puntos > **Settings** > **Secrets** |

## Tarea (1 hora como máximo)

1. **Tus consultas:** agrega 3 consultas propias a `consultas_del_dia.json` (una que tenga que ir para Marta y una inválida a propósito), procésalas y revisa `pipeline.log`. ¿Rayo las clasificó como esperabas?
2. **Opcional:** publica tu Rayo con la guía de arriba.
3. Leer en la plataforma "Aplicaciones inteligentes con Python e interfaces interactivas" (Módulo 6).
