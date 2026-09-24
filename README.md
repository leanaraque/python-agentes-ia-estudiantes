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
- `final/`: el código como quedó al terminar la clase.

Las carpetas se publican a medida que avanza el curso.
