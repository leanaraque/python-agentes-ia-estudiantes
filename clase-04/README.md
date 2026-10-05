# Clase 4 · Respuestas en las que se puede confiar

Hoy el asistente de **Rodados Sur** deja de devolver texto libre: el modelo analiza cada consulta y responde en **JSON** (intención, urgencia, confianza y respuesta). Python valida ese JSON y decide qué hacer. Si el modelo no tiene el dato, dice **DESCONOCIDO** y el asistente deriva a Marta en lugar de inventar.

Además, el mismo código puede usar un modelo en la nube (Groq) o un modelo **en tu computadora** (Ollama), cambiando una sola línea del `.env`.

## Qué vimos

- **Por qué estructurar la salida:** cuando la respuesta la usa un programa, necesita un formato predecible.
- **JSON y `json.loads`:** el modelo siempre devuelve texto; `json.loads` lo convierte en `dict`.
- **Validar el formato:** `parse_json` busca el JSON aunque venga con texto alrededor; si falla, se le pide al modelo que lo corrija una vez.
- **Validar el contenido:** `validate_analysis` controla que las claves existan y que los valores sean los permitidos.
- **Patrón DESCONOCIDO:** "no sé" es una respuesta válida; inventar, no.
- **Modelos locales:** privacidad, sin internet y sin costo por uso, a cambio de menos calidad y de depender del hardware.

## Archivos

| Carpeta | Contenido |
|---|---|
| [`inicio/`](./inicio) | El proyecto como terminó la Clase 3 |
| [`pasos/`](./pasos) | El proyecto completo en cada paso de la clase (`paso-1` a `paso-4`) |
| [`final/`](./final) | El proyecto terminado, **comentado línea por línea** |

## Armar la carpeta de la clase

Desde la carpeta del curso (la que contiene a `clase-03`):

```powershell
New-Item -ItemType Directory clase-04
Copy-Item clase-03\*.py, clase-03\requirements.txt, clase-03\.env, clase-03\.env.example, clase-03\.gitignore clase-04
```

En VS Code: **File > Open Folder** > `clase-04`, y en una terminal nueva:

```powershell
python -m venv .venv
.venv\Scripts\Activate.ps1
python -m pip install -r requirements.txt
```

Por último: **Ctrl + Shift + P** > `Python: Select Interpreter` > **('.venv': venv)**.

### El `.env` de esta clase

Al `.env` de la Clase 3 se le suman dos líneas (paso 4): `LLM_PROVIDER=groq` y `OLLAMA_MODEL=qwen2.5:1.5b`. Con `LLM_PROVIDER=groq` todo funciona como en la Clase 3, sin instalar nada.

## Cómo probarlo

```powershell
python assistant.py
```

| Escribe | Qué pasa |
|---|---|
| `¿A qué hora abren el sábado?` | Responde con el horario |
| `¿Conviene salir a pedalear hoy?` | Consulta el clima: el modelo detectó la intención, sin la palabra "clima" |
| `Se me rompió la cadena y la necesito mañana para trabajar` | Responde y avisa que, como es urgente, Marta te contacta hoy |
| `¿Venden cascos?` | "No tengo ese dato. Se lo paso a Marta": ya no inventa |
| `¿Quién ganó el último mundial?` | No es del negocio: deriva a Marta |

Las respuestas del modelo pueden variar en cada ejecución.

## Tarea: un modelo en tu computadora con Ollama (opcional, recomendada)

Necesitas alrededor de 5 GB libres en el disco. Funciona sin placa de video (más lento).

1. **Instalar Ollama.** En PowerShell (no pide permisos de administrador):

   ```powershell
   irm https://ollama.com/install.ps1 | iex
   ```

   Alternativa: descargar `OllamaSetup.exe` desde [ollama.com/download](https://ollama.com/download) e instalarlo.

2. **Abrir una terminal nueva** y verificar:

   ```powershell
   ollama --version
   ```

3. **Descargar el modelo** (alrededor de 1 GB):

   ```powershell
   ollama pull qwen2.5:1.5b
   ```

   Si tu conexión es lenta, puedes usar `gemma3:1b` (815 MB) y poner ese nombre en `OLLAMA_MODEL`.

4. **Probarlo en la terminal** (sin internet). Se sale con `/bye`:

   ```powershell
   ollama run qwen2.5:1.5b
   ```

5. **Usarlo desde el asistente:** en el `.env`, cambia a `LLM_PROVIDER=ollama`, guarda y ejecuta `python assistant.py`.

6. Anota: ¿cuánto tarda en responder?, ¿responde igual de bien que Groq?, ¿aparece algún "Error controlado" por un JSON mal formado?

7. Vuelve a `LLM_PROVIDER=groq` para la próxima clase.

### Problemas frecuentes

| Síntoma | Solución |
|---|---|
| `ollama` no se reconoce como comando | Cerrar la terminal y abrir una nueva después de instalar |
| `Error controlado: no pude hablar con el modelo (... localhost ... 11434 ...)` | Ollama no está corriendo: abre la aplicación Ollama desde el menú Inicio |
| `Error controlado: el modelo no devolvió un JSON válido.` | Los modelos chicos fallan más con el formato: vuelve a preguntar o usa Groq |
| Responde muy lento | Normal en computadoras sin placa de video: es el costo de correr el modelo en tu equipo |

## Tarea (1 hora como máximo)

1. Opcional pero recomendado: la guía de Ollama de arriba.
2. Agregar al prompt una regla nueva para un caso que hoy responda mal (por ejemplo, consultas sobre una orden de reparación) y comprobar el resultado.
3. Leer en la plataforma "Modelos de lenguaje y agentes" (Módulo 2), la parte de agentes con memoria y funciones.
