# Python para Desarrollo de Agentes con IA

Material de clase del curso "Python con IA: Desarrollo de Agentes y Aplicaciones Inteligentes" de Educación IT.

Durante el curso vamos a construir, clase a clase, **un asistente virtual para Rodados Sur**, una tienda y taller de bicicletas de barrio que recibe todos los días las mismas consultas. Empieza respondiendo con reglas simples y termina siendo un agente que conversa, usa herramientas, escucha, habla y funciona en la web.

## Antes de la primera clase

1. Instalar **Python 3.12** desde [python.org](https://www.python.org/downloads/). En Windows, marcar la casilla **"Add python.exe to PATH"** durante la instalación.
2. Instalar **Visual Studio Code** desde [code.visualstudio.com](https://code.visualstudio.com/).
3. En VS Code, instalar la extensión **Python** (de Microsoft).
4. Verificar en una terminal:

   ```bash
   python --version
   ```

   Tiene que mostrar `Python 3.12.x`.

## Descargas y documentación

| Herramienta | Descarga | Documentación |
|---|---|---|
| Python 3.12 | [python.org/downloads](https://www.python.org/downloads/) | [Tutorial oficial en español](https://docs.python.org/es/3/tutorial/) |
| VS Code | [code.visualstudio.com](https://code.visualstudio.com/) | [Documentación de VS Code](https://code.visualstudio.com/docs) |
| Extensión Python | Dentro de VS Code: Extensiones > buscar "Python" (Microsoft) | [Python en VS Code](https://code.visualstudio.com/docs/python/python-tutorial) |

### Problemas frecuentes al instalar (Windows)

| Síntoma | Solución |
|---|---|
| `python` no se reconoce como comando | Reinstalar Python marcando **"Add python.exe to PATH"**. Mientras tanto, probar `py --version`. |
| Al escribir `python` se abre la Microsoft Store | Buscar en Windows "Administrar alias de ejecución de aplicaciones" y desactivar los de Python. |
| En macOS, `python` no existe | Usar `python3` en lugar de `python`. |

## Cómo está organizado

Cada clase tiene su carpeta (`clase-01`, `clase-02`, ...) con:

- `README.md`: qué hicimos y los pasos para repetirlo.
- `inicio/`: el código con el que arranca la clase.
- `pasos/`: el proyecto completo en cada paso.
- `final/`: el código como quedó al terminar la clase, comentado.

## Las clases

| Clase | Tema | Rayo aprende a... |
|---|---|---|
| [1](./clase-01) | Python como capa de control | Responder con reglas |
| [2](./clase-02) | Entorno, variables de entorno y APIs | Vivir en un proyecto y consultar el clima |
| [3](./clase-03) | Modelos de lenguaje y prompts | Pensar con un modelo de lenguaje (Groq) |
| [4](./clase-04) | Respuestas estructuradas y LLM local | Responder en JSON validado y decir DESCONOCIDO |
| [5](./clase-05) | Agentes: memoria y herramientas | Recordar y usar herramientas |
| [6](./clase-06) | IA conversacional y voz | Escuchar y hablar |
| [7](./clase-07) | Contenido multimedia y ética | Crear una promo: guion, imagen, audio y video |
| [8](./clase-08) | Pipelines, nube y Streamlit | Procesar las consultas del día y estar en la web |
| [9](./clase-09) | Aplicaciones inteligentes | Ser una app de soporte: memoria, errores y Marta en el circuito |

El `README.md` del proyecto terminado (arquitectura, cómo ejecutarlo y reflexión técnica) está en [`clase-09/final/README.md`](./clase-09/final/README.md).
