# Clase 5 · De asistente a agente

Hoy el asistente de **Rodados Sur** se convierte en un **agente**: recuerda la conversación y decide solo cuándo usar herramientas para consultar una orden del taller, ver el clima o derivar una consulta a Marta.

## Qué vimos

- **Agente** = modelo de lenguaje + rol e instrucciones + memoria + herramientas + bucle de control.
- **Memoria de corto plazo:** el modelo no recuerda nada por sí mismo; la memoria es la lista de mensajes que le reenviamos completa en cada llamada. Por eso **cuesta tokens**: en la prueba del curso, 5 consultas fueron 7 llamadas y unos 4.950 tokens.
- **Otros tipos de memoria:** de largo plazo (datos que persisten), vectorial o RAG (buscar en documentos) y procedimental (pasos de tareas largas).
- **Herramientas (*function calling*):** una función de Python más una ficha (`name`, `description`, `parameters`) que el modelo lee. **El modelo no ejecuta nada: pide.** Python ejecuta y le devuelve el resultado.
- **El bucle del agente:** preguntar al modelo; si pide herramientas, ejecutarlas y devolver los resultados; si responde, terminar. Con un límite de vueltas.

## Archivos

| Carpeta | Contenido |
|---|---|
| [`inicio/`](./inicio) | El proyecto como terminó la Clase 4 |
| [`pasos/`](./pasos) | El proyecto completo en cada paso de la clase (`paso-1` a `paso-4`) |
| [`final/`](./final) | El proyecto terminado, **comentado línea por línea** |

Archivos nuevos de esta clase: `prueba_memoria.py`, `ordenes.json`, `tools.py` y `prueba_herramientas.py`. El agente escribe `derivaciones.json` cuando deriva una consulta a Marta.

## Armar la carpeta de la clase

Desde la carpeta del curso (la que contiene a `clase-04`):

```powershell
New-Item -ItemType Directory clase-05
Copy-Item clase-04\*.py, clase-04\requirements.txt, clase-04\.env, clase-04\.env.example, clase-04\.gitignore clase-05
```

En VS Code: **File > Open Folder** > `clase-05`, y en una terminal nueva:

```powershell
python -m venv .venv
.venv\Scripts\Activate.ps1
python -m pip install -r requirements.txt
```

Por último: **Ctrl + Shift + P** > `Python: Select Interpreter` > **('.venv': venv)**. Revisa que el `.env` tenga `LLM_PROVIDER=groq`.

**¿No tienes la carpeta de la Clase 4?** Copia el contenido de [`inicio/`](./inicio) en una carpeta `clase-04` y crea su `.env` a partir de `.env.example` (una variable por línea, con tu clave de Groq).

## Cómo probarlo

```powershell
python assistant.py
```

Escribe las consultas **una por una, sin apuro**:

| Escribe | Qué pasa |
|---|---|
| `Hola, soy Ana. ¿Cómo va mi bici?` | Pide el número de orden |
| `Es la orden 1043.` | Usa `get_order_status`: en reparación, lista el lunes |
| `¿Y para cuándo estaría lista?` | Responde con la memoria, sin herramientas |
| `¿Conviene salir a pedalear hoy?` | Usa `get_weather` |
| `¿Venden cascos?` | Usa `hand_off_to_marta`: no tiene el dato |
| `¿Cómo me llamo?` | "Te llamas Ana" |

En la terminal vas a ver cada herramienta que usa: `[herramienta] get_order_status {"order_id":"1043"}`.

### Problemas frecuentes

| Síntoma | Solución |
|---|---|
| `429 Client Error: Too Many Requests` | Superaste el límite gratuito de tokens por minuto (la memoria reenvía toda la conversación). Espera un minuto y sigue: la conversación no se pierde |
| `FileNotFoundError: ... ordenes.json` | `ordenes.json` tiene que estar en la misma carpeta que `tools.py` |
| Un error de sintaxis en `tools.py` | Suele faltar una coma o una llave en `TOOLS`: copia el archivo de `pasos/paso-2` |
| `Error controlado: no pude hablar con el modelo (... 11434 ...)` | El `.env` quedó con `LLM_PROVIDER=ollama`: cámbialo a `groq` |

## Tarea (1 hora como máximo)

1. **Agregar una herramienta nueva** a `tools.py`: `calculate_rental_cost(days)`, que calcule el costo de alquilar una bici urbana (`days * 8000`). Hace falta:
   - la función;
   - su ficha en `TOOLS`, con el parámetro `days` de tipo `"integer"`;
   - un `if` más en `execute_tool`.

   Probar con "¿Cuánto me sale alquilar una bici por 3 días?".
2. Anotar una conversación en la que el agente se haya equivocado y por qué crees que pasó.
3. Leer en la plataforma "IA conversacional y voz" (Módulo 3).
