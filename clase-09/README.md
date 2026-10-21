# Clase 9 · Una app de soporte de verdad

La última clase. La app web de Rayo se vuelve un **sistema de soporte**: un chat que **recuerda**, que **no se cae** cuando algo falla y que **le pasa a Marta** lo que no sabe, con el contacto del cliente y un panel con clave. Al final, el proyecto queda documentado en un README y presentado.

## Qué vimos

- **Aplicaciones inteligentes:** una interfaz, una lógica que decide, uno o varios modelos y una salida comprensible. El usuario no percibe el modelo, solo la funcionalidad. **Streamlit** (apps de datos y prototipos) y **Gradio** (probar un modelo).
- **Un chat con memoria:** Streamlit vuelve a ejecutar el archivo en cada clic; **`st.session_state`** conserva la conversación (una por persona). `st.chat_message` y `st.chat_input` arman el chat. El agente de la Clase 5 no cambia.
- **La memoria cuesta:** cada mensaje reenvía toda la conversación. Medido: 5 preguntas, 8 llamadas y unos 7.000 tokens (el plan gratuito de Groq da 8.000 por minuto).
- **Errores y control de flujo:** si el modelo falla, el cliente recibe una **respuesta alternativa** armada con el `FAQ` (sin IA), el error queda en el registro y la consulta pasa a Marta. La app nunca se cae.
- **Soporte con control humano:** antes de derivar, Rayo pide **nombre y teléfono** (funciona gracias a la memoria). Marta ve las derivaciones en un **panel con clave** (`MARTA_PASSWORD`). Medido: deriva con el contacto 8 de 8 veces, pero 1 de 8 inventó que venden cascos: por eso una persona revisa.
- **Documentar y presentar:** el `README.md` del proyecto (la Etapa 6) y cómo presentar un proyecto en 2 minutos.

## Archivos

| Carpeta | Contenido |
|---|---|
| [`inicio/`](./inicio) | El proyecto como terminó la Clase 8 |
| [`pasos/`](./pasos) | El proyecto completo en cada paso de la clase (`paso-1` a `paso-4`) |
| [`final/`](./final) | El proyecto terminado, con `app.py`, `tools.py`, `assistant.py` y `pipeline.py` **comentados línea por línea**, y el `README.md` del proyecto |

Hoy no hay archivos nuevos de Python: cambian `app.py` (pasos 1 a 3), `tools.py` y `assistant.py` (paso 3). El archivo nuevo es `README.md` (paso 4). **No hay librerías nuevas.**

## Armar la carpeta de la clase

Desde la carpeta del curso (la que contiene a `clase-08`):

```powershell
New-Item -ItemType Directory clase-09
Copy-Item clase-08\*.py, clase-08\ordenes.json, clase-08\consultas_del_dia.json, clase-08\requirements.txt, clase-08\.env, clase-08\.env.example, clase-08\.gitignore clase-09
```

Hoy `requirements.txt` **se copia**: es el que descargaste en la Clase 8. En VS Code: **File > Open Folder** > `clase-09`. En una terminal nueva:

```powershell
python -m venv .venv
.venv\Scripts\Activate.ps1
python -m pip install -r requirements.txt
```

**La clave del panel de Marta.** Agrega una variable al `.env` sin abrirlo (cambia `bicis-de-marta` por la clave que quieras, sin espacios; ejecútalo una sola vez):

```powershell
Add-Content .env "`nMARTA_PASSWORD=bicis-de-marta"
```

Para comprobar que todo está bien:

```powershell
python -c "import sys, os, dotenv, streamlit; dotenv.load_dotenv(); print(sys.prefix); print('Clave de Groq cargada:', bool(os.getenv('GROQ_API_KEY'))); print('Clave de Marta cargada:', bool(os.getenv('MARTA_PASSWORD'))); print('Streamlit', streamlit.__version__); print('Entorno listo')"
```

Tiene que mostrar la ruta de la caja (termina en `clase-09\.venv`), `Clave de Groq cargada: True`, `Clave de Marta cargada: True`, `Streamlit 1.50.0` y `Entorno listo`.

Por último: **Ctrl + Shift + P** > `Python: Select Interpreter` > **('.venv': venv)**.

**¿No tienes la carpeta de la Clase 8?** Copia el contenido de [`inicio/`](./inicio) en una carpeta `clase-08`, crea su `.env` a partir de `.env.example` (una variable por línea, con tu clave de Groq) y descarga el `requirements.txt` de la Clase 8:

```powershell
Invoke-WebRequest https://raw.githubusercontent.com/leanaraque/python-agentes-ia-estudiantes/main/clase-08/requirements.txt -OutFile requirements.txt -UseBasicParsing
```

## Cómo probarlo

La app se ejecuta con Streamlit (**no** con `python app.py`):

```powershell
python -m streamlit run app.py
```

Se abre en `http://localhost:8501`. La terminal queda ocupada: no está trabada, está sirviendo la página. Para detenerla: **Ctrl + C**.

### El chat con memoria (paso 1)

1. Escribe en la caja de abajo "Hola, me llamo Laura." y después "¿Cómo me llamo?": responde "Te llamas Laura." (en la Clase 8 no lo sabía).
2. Mira el contador de abajo: cuántos mensajes viajan al modelo en cada consulta.
3. **Nueva conversación** vacía la memoria. Si abres la página en otra pestaña del navegador, es otra persona: otra memoria.

### El error a propósito (paso 2)

Para ver qué pasa si el modelo falla, levanta la app con una **clave falsa** solo en esa terminal (el `.env` no se toca):

```powershell
$env:GROQ_API_KEY = "clave-de-prueba"; python -m streamlit run app.py
```

Pregunta algo: Rayo responde "En este momento no puedo responder, pero dejé tu consulta para Marta..." con la dirección y el horario. En la terminal aparece la línea `WARNING ... 401 Client Error: Unauthorized` (también queda en `pipeline.log`) y la consulta queda en `derivaciones.json`. Para volver a la clave buena:

```powershell
Remove-Item Env:GROQ_API_KEY; python -m streamlit run app.py
```

### Marta en el circuito (paso 3)

1. Pregunta "¿Venden cascos?": Rayo te pide nombre y teléfono. Respóndele (con datos inventados) y deriva la consulta a Marta.
2. Pestaña **Panel de Marta**: escribe tu `MARTA_PASSWORD`. Aparecen las derivaciones (con el contacto) y las consultas del día.

**¿Agregaste una herramienta propia en `tools.py`** (por ejemplo, la tarea de la Clase 5)? En el paso 3 no reemplaces el archivo entero: aplica solo los cambios de `hand_off_to_marta` (el parámetro `contact`).

### El README del proyecto (paso 4)

Crea `README.md` y pega el del paso 4 ([`pasos/paso-4/README.md`](./pasos/paso-4/README.md)):

```powershell
New-Item README.md; code README.md
```

En VS Code, **Ctrl + Shift + V** muestra la vista previa. El diagrama se dibuja en GitHub, no en VS Code.

## Actualizar tu app publicada (opcional)

Si publicaste tu Rayo en la Clase 8:

1. Dentro de `clase-09`, arma la carpeta `publicar` (hoy con `README.md`, 12 archivos) y ábrela:

   ```powershell
   New-Item -ItemType Directory publicar; Copy-Item app.py, pipeline.py, assistant.py, llm_client.py, tools.py, weather.py, speech_input.py, speech_output.py, ordenes.json, consultas_del_dia.json, requirements.txt, README.md publicar
   Invoke-Item publicar
   ```

2. En tu repositorio de GitHub: **Add file** > **Upload files**, arrastra los 12 archivos y **Commit changes**. Los archivos con el mismo nombre se reemplazan.

3. **Los secretos:** copia las variables del `.env` al portapapeles (hoy son 6, con `MARTA_PASSWORD`; no muestra las claves):

   ```powershell
   $secrets = Get-Content .env | Where-Object { $_ -match '^(GROQ_API_KEY|GROQ_MODEL|ASSISTANT_NAME|WEATHER_LATITUDE|WEATHER_LONGITUDE|MARTA_PASSWORD)=' } | ForEach-Object { $name, $value = $_ -split '=', 2; "$name = `"$($value.Trim())`"" }; $secrets | Set-Clipboard; "Variables copiadas: $($secrets.Count)"
   ```

   En tu app: **Manage app** > los tres puntos > **Settings** > **Secrets**. Selecciona todo (**Ctrl + A**), pega (**Ctrl + V**) y **Save**.

4. La app toma el código nuevo sola. Si en un par de minutos no ves la pestaña **Panel de Marta**: **Manage app** > los tres puntos > **Reboot app**.

**Ojo:** la app es pública y usa tu clave de Groq. Cuando ya no la uses, en `share.streamlit.io`: los tres puntos de la app > **Delete**.

## Problemas frecuentes

| Síntoma | Solución |
|---|---|
| Rayo no recuerda | `app.py` tiene que ser idéntico al del paso: falta `if "messages" not in st.session_state:` |
| El mensaje aparece debajo de la caja de chat | Falta `with chat:` antes de mostrarlo |
| `Clave de Marta cargada: False` | Falta el comando `Add-Content` de "Armar la carpeta" |
| "La clave no es correcta." con la clave buena | La app se levantó antes de agregar `MARTA_PASSWORD`: Ctrl + C y vuelve a ejecutarla |
| `TypeError: hand_off_to_marta() missing 1 required positional argument: 'contact'` | `tools.py` y `app.py` tienen que ser del mismo paso |
| Rayo pide el teléfono cuando solo saludas | Falta la última regla del prompt de `assistant.py` (paso 3) |
| `Remove-Item : Cannot find path 'Env:GROQ_API_KEY'` | No pasa nada: esa terminal no tenía la clave falsa. La app arranca igual |
| La respuesta alternativa aparece sin haber puesto una clave falsa | Límite por minuto de Groq (429): la memoria reenvía toda la conversación. Espera un minuto o usa **Nueva conversación** |
| `ModuleNotFoundError: No module named 'streamlit'` | La caja no está activa o faltó `python -m pip install -r requirements.txt` |

## Tarea final (1 hora como máximo)

1. **Tu README (la Etapa 6):** adapta el `README.md` a tu asistente: su nombre, lo que agregaste (tu herramienta, un desafío extra, tu promo) y tu propia reflexión técnica: qué escalarías y qué mejorarías.
2. **Opcional:** publica o actualiza tu app con la guía de arriba y comparte el link.
3. Leer en la plataforma "¿Cómo continuar?".

## Cómo seguir

- **RAG:** que el agente lea documentos del negocio (la memoria de largo plazo de la Clase 5).
- **LangChain y otros frameworks de agentes:** hacen lo que escribimos a mano en `run_agent`; ahora sabes qué hay adentro.
- **Voz en tiempo real:** los modelos de voz a voz de la Clase 6.
- **Bases de datos y usuarios:** lo que le falta a Rayo para guardar en serio.
