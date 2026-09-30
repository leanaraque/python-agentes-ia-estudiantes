# Clase 3 · El asistente empieza a pensar

Hoy el asistente de **Rodados Sur** deja de buscar palabras clave y empieza a responder con un **modelo de lenguaje real** (Groq). Le damos instrucciones con un *prompt* que describe el negocio, y todo lo que habla con el modelo queda en un módulo propio: `llm_client.py`.

Corresponde a la **Etapa 2 del Proyecto Integrador** (consumo real de una API de lenguaje).

## Qué vimos

- **Modelo de lenguaje:** predice el siguiente *token* (pedacito de palabra) según probabilidades. Por eso escribe bien... y por eso puede **inventar** (alucinar).
- **Temperature:** baja = respuestas estables; alta = más variedad (y más errores).
- **API de un modelo:** una request `POST` con la clave en los *headers* y una lista de `messages` en el cuerpo. La respuesta trae el texto en `choices[0]["message"]["content"]` y los tokens usados en `usage`.
- **Prompt:** rol, tarea, contexto, restricciones y formato. Va en el mensaje `system`; la consulta del cliente, en el mensaje `user`.
- **`llm_client.py`:** una pieza que solo habla con el modelo y maneja sus errores (`MissingAPIKeyError`, `ConnectionError`, `ValueError`).

## Archivos

| Carpeta | Contenido |
|---|---|
| [`inicio/`](./inicio) | El proyecto como terminó la Clase 2 |
| [`pasos/`](./pasos) | El proyecto completo en cada paso de la clase (`paso-1` a `paso-4`) |
| [`final/`](./final) | El proyecto terminado, **comentado línea por línea** |

## Armar la carpeta de la clase

Trabajamos una carpeta por clase. En la terminal, parado en la carpeta del curso (la que contiene a `clase-02`):

```powershell
New-Item -ItemType Directory clase-03
Copy-Item clase-02\*.py, clase-02\requirements.txt, clase-02\.env, clase-02\.env.example, clase-02\.gitignore clase-03
```

Después, en VS Code: **File > Open Folder** > `clase-03`, y en una terminal nueva:

```powershell
python -m venv .venv
.venv\Scripts\Activate.ps1
python -m pip install -r requirements.txt
```

Por último: **Ctrl + Shift + P** > `Python: Select Interpreter` > **('.venv': venv)**.

### El `.env` de esta clase

Al `.env` de la Clase 2 se le suman dos líneas: `GROQ_API_KEY=` seguido de tu clave (la de la tarea) y `GROQ_MODEL=openai/gpt-oss-20b`. **Tu clave es privada:** no la compartas, no la pegues en el chat y no la subas a GitHub.

Si todavía no tienes clave: entra en [console.groq.com/keys](https://console.groq.com/keys), crea una y pégala en el `.env` (se muestra una sola vez).

### Problemas frecuentes

| Síntoma | Solución |
|---|---|
| `MissingAPIKeyError: falta GROQ_API_KEY` | La línea no está en el `.env`, está comentada o el `.env` no se copió a `clase-03` |
| `401 Client Error: Unauthorized` | La clave está mal copiada (sobra un espacio, falta una letra) o fue eliminada en la consola de Groq |
| `429 Client Error: Too Many Requests` | Superaste el límite gratuito por minuto: espera un minuto y vuelve a probar |
| `404` o `400` al cambiar `GROQ_MODEL` | Ese modelo no existe o no está en tu plan: vuelve a `openai/gpt-oss-20b` |
| `RequestsDependencyWarning` al ejecutar | La ruta de la carpeta es demasiado larga para Windows: mueve el curso a una carpeta más corta (por ejemplo, `C:\curso`) |

## Cómo probarlo

```powershell
python assistant.py
```

| Escribe | Qué pasa |
|---|---|
| `¿A qué hora abren?` | Responde el horario: ahora **entiende la intención**, aunque no esté la palabra "horario" |
| `¿Llueve hoy?` | Sigue respondiendo con la API del clima |
| `¿Quién ganó el último mundial?` | No es del negocio: te deriva a Marta |
| `¿Venden cascos?` | A veces **inventa** una respuesta: es una alucinación (la controlamos en la Clase 4) |

Las respuestas del modelo cambian en cada ejecución.

## Tarea (1 hora como máximo)

1. Agregar al prompt de `build_system_prompt()` **un ejemplo** de pregunta y respuesta ideal (*few-shot*) y comprobar si cambia el estilo del asistente.
2. Hacer 5 preguntas reales al asistente y anotar **cuál respondió mal o inventó algo**.
3. Opcional: cambiar en el `.env` `GROQ_MODEL=openai/gpt-oss-120b` y comparar las respuestas. Después volver a `openai/gpt-oss-20b`.
4. Leer en la plataforma "Respuestas estructuradas y confiables" (Módulo 2).
