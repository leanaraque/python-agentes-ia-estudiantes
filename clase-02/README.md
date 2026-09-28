# Clase 2 · Un proyecto profesional que habla con el mundo

Hoy el asistente de **Rodados Sur** se muda a un proyecto profesional: tiene su propio entorno virtual, sus dependencias en una lista y su configuración afuera del código. Además, aprende a responder "¿llueve hoy?" consultando una API real de clima.

Con esta clase queda completa la **Etapa 1 del Proyecto Integrador** (consignas 1 y 2: entorno virtual y `ASSISTANT_NAME` en una variable de entorno).

## Qué vimos

- **Entorno virtual:** una caja aislada con las librerías del proyecto (`.venv`) y la lista para rearmarla (`requirements.txt`).
- **Configuración y secretos:** el código no guarda nombres, coordenadas ni claves. Todo va en `.env`, que **nunca** se sube a GitHub (`.gitignore`). Lo que se comparte es `.env.example`.
- **API:** una puerta controlada a otro sistema. Request (método, URL, parámetros, headers) y response (código de estado y JSON).
- **JSON y `dict`:** `response.json()` convierte la respuesta en un `dict`. Se lee con corchetes: `data["current"]["temperature_2m"]`. En Python, `data.current` da error.
- **`requests`:** la librería para hablar con APIs desde Python.
- **Módulos:** `weather.py` hace una sola cosa (consultar el clima) y `assistant.py` lo importa.

## Archivos

| Carpeta | Contenido |
|---|---|
| [`inicio/`](./inicio) | El `assistant.py` con el que termina la Clase 1 |
| [`pasos/`](./pasos) | El proyecto completo en cada paso de la clase (`paso-1` a `paso-4`). Si te perdiste, copia los archivos del paso y sigue desde ahí. |
| [`final/`](./final) | El proyecto terminado, **comentado línea por línea** para repasar en casa |
| [`desafio/`](./desafio) | Desafío extra opcional: guardar la respuesta de la API en un archivo JSON con la fecha |

### El `.env` de cada paso

El `.env` no se sube a GitHub, así que tienes que crearlo a mano en la carpeta del proyecto (al lado de `assistant.py`). Su contenido en cada paso:

| Paso | Contenido del `.env` |
|---|---|
| 1 y 2 | `ASSISTANT_NAME=` y el nombre de tu asistente |
| 3 y 4 | Lo anterior, más `WEATHER_LATITUDE=-34.61` y `WEATHER_LONGITUDE=-58.38` (una variable por línea) |

## Cómo armar el proyecto desde cero

En la terminal de VS Code, dentro de la carpeta del proyecto:

```powershell
python -m venv .venv
.venv\Scripts\Activate.ps1
python -m pip install -r requirements.txt
```

En macOS o Linux, la activación es `source .venv/bin/activate` (y puede ser `python3` en lugar de `python`).

Después: **Ctrl + Shift + P** > `Python: Select Interpreter` > el que dice **('.venv': venv)**.

### Problemas frecuentes

| Síntoma | Solución |
|---|---|
| "La ejecución de scripts está deshabilitada" al activar | Correr una vez `Set-ExecutionPolicy -ExecutionPolicy RemoteSigned -Scope CurrentUser` y volver a activar |
| `pip` no se reconoce como comando | Usar `python -m pip` |
| `ModuleNotFoundError: No module named 'dotenv'` | La caja no está activa o VS Code usa otro intérprete: activarla, elegir el intérprete `.venv` y reinstalar |
| El `.env` no se lee | El archivo tiene que llamarse exactamente `.env` (no `.env.txt`) y estar al lado de `assistant.py`. Crearlo desde VS Code. |
| `curl` da un error raro en PowerShell | Escribir `curl.exe` |

## Cómo probarlo

```powershell
python assistant.py
```

| Escribe | Qué pasa |
|---|---|
| `¿Llueve hoy?` | Responde la temperatura, la probabilidad de lluvia y un consejo |
| `¿Cuál es el horario?` | Responde con el FAQ, como en la Clase 1 |
| (sin internet) `clima` | Muestra un error controlado y sigue funcionando |
| `salir` | Se despide |

## Tarea (1 hora como máximo)

1. **Crear una cuenta gratuita en Groq** y una API key:
   - Entrar en [console.groq.com](https://console.groq.com) e iniciar sesión.
   - Ir a **API Keys** ([console.groq.com/keys](https://console.groq.com/keys)) y crear una clave.
   - La clave se muestra **una sola vez**: cópiala y pégala en tu `.env` como una línea nueva: `GROQ_API_KEY=` seguido de la clave.
   - No la compartas con nadie, no la pegues en el chat y no la subas a GitHub.
2. Agregar `GROQ_API_KEY=` (sin valor) a tu `.env.example`.
3. Traer anotadas las tres preguntas que el asistente no supo responder (tarea de la Clase 1).
4. Opcional: el [desafío](./desafio) de guardar el clima en un archivo JSON.
5. Leer en la plataforma "Modelos de lenguaje y agentes" (Módulo 2).
