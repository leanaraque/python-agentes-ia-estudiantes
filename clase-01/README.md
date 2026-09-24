# Clase 1 · Tu primer asistente (sin IA todavía)

Hoy construimos la primera versión del asistente de **Rodados Sur**: responde las preguntas frecuentes del negocio con reglas simples y no se rompe ante un error. Todavía no usa inteligencia artificial; eso llega en la Clase 3.

Corresponde a la **Etapa 1 del Proyecto Integrador** (consignas 3, 4 y 5). Las consignas 1 y 2 (entorno virtual y variable de entorno) las hacemos en la Clase 2.

## Qué vimos

- Por qué Python es el lenguaje de la IA: es la **capa de control** que dirige a los modelos.
- **Variables y tipos:** `str`, `int`, `float`, `bool`, `list` y `dict`.
- **Estructuras de control:** `if` para decidir, `for` y `while` para repetir.
- **Funciones:** una pieza, una tarea. Reciben algo y devuelven algo.
- **Excepciones:** `raise`, `try` y `except` para que el asistente siga funcionando cuando algo sale mal.

## Archivos

| Carpeta | Contenido |
|---|---|
| [`inicio/`](./inicio) | El punto de partida: el diccionario de preguntas frecuentes listo para copiar |
| [`final/`](./final) | `assistant.py` como quedó al terminar la clase |

## Cómo ejecutarlo

1. Abrir la carpeta del proyecto en VS Code (**File > Open Folder**).
2. Abrir la terminal (**Terminal > New Terminal**).
3. Ejecutar:

   ```bash
   python assistant.py
   ```

4. Probar con estas consultas:

   | Escribe | Qué pasa |
   |---|---|
   | `¿Cuál es el horario?` | Responde el horario del local |
   | `Quiero hacer un service` | Responde los precios |
   | (Enter sin escribir nada) | Muestra un error controlado y sigue funcionando |
   | `¿A qué hora abren?` | No entiende: las reglas solo comparan palabras (lo resolvemos en la Clase 3) |
   | `salir` | Se despide y dice cuántas consultas respondió |

## Tarea

1. Agregar al `FAQ` dos preguntas nuevas de Rodados Sur (por ejemplo, `"garantía"` y `"pago"`).
2. Anotar **tres preguntas reales** que el asistente no pudo responder. Las vamos a usar en la Clase 3.
3. Leer en la plataforma "Entornos modernos" (Módulo 1).
