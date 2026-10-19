# app.py, paso 4: dos pestañas. Una para los clientes (el agente, como en el paso 3)
# y otra para Marta: procesa las consultas del día con el pipeline y muestra el reporte.
# La misma lógica (pipeline.py) sirve para la terminal y para la web.
import json

# Streamlit convierte un programa de Python en una página web, sin escribir HTML.
# "as st" es un apodo: en lugar de streamlit.title escribimos st.title.
import streamlit as st

# El agente de la Clase 5, tal cual: sus instrucciones y su bucle con herramientas.
from assistant import ASSISTANT_NAME, build_system_prompt, run_agent
from llm_client import MissingAPIKeyError
# El pipeline de hoy: la web reusa las mismas funciones que la terminal.
from pipeline import QUERIES_FILE, load_queries, run_pipeline

# Las columnas de la tabla, en este orden (las demás no se muestran).
RESULT_COLUMNS = ("id", "canal", "estado", "mensaje", "respuesta", "detalle")


# Muestra el reporte en la página. Las funciones ayudan a leer el archivo por partes.
def show_report(results, metadata):
    """Muestra el reporte del pipeline: los números del día, la tabla y el botón para descargarlo."""
    counts = metadata["por_estado"]
    # st.columns(4) divide el ancho en cuatro columnas; metric muestra un número grande con su título.
    col1, col2, col3, col4 = st.columns(4)
    col1.metric("Listas", counts.get("lista", 0))
    col2.metric("Para Marta", counts.get("para Marta", 0))
    col3.metric("Inválidas", counts.get("inválida", 0))
    col4.metric("Con error", counts.get("error", 0))
    st.caption(f"{metadata['total']} consultas en {metadata['segundos']} s. Reporte guardado en {metadata['carpeta']}")
    # Una tabla interactiva a partir de la lista de dicts: cada dict es una fila.
    # Se puede ordenar con un clic en la columna y agrandar con el botón de pantalla completa.
    st.dataframe(results, column_order=RESULT_COLUMNS, hide_index=True)
    report = json.dumps(results, ensure_ascii=False, indent=2)
    # Un botón que descarga el texto como archivo. En la nube, el disco del servidor es temporal:
    # descargar el reporte es la forma de quedárselo.
    st.download_button("Descargar resultados (JSON)", report, file_name="resultados.json")


# El título de la pestaña del navegador. layout="wide": usa todo el ancho (para la tabla).
st.set_page_config(page_title="Rodados Sur", layout="wide")
# IMPORTANTE: Streamlit ejecuta este archivo de arriba a abajo cada vez que alguien
# toca algo en la página (un botón, por ejemplo). No hay un bucle while como en la terminal.
st.title(f"{ASSISTANT_NAME}, el asistente de Rodados Sur")
# Dos pestañas. Lo que se escribe dentro de "with client_tab:" aparece en la primera.
client_tab, marta_tab = st.tabs([f"Preguntar a {ASSISTANT_NAME}", "Consultas del día"])

with client_tab:
    st.write("Pregunta por horarios, precios, el estado de tu orden o el clima para salir en bici.")
    # Un cuadro de texto. Devuelve lo que escribió la persona (o "" si está vacío).
    question = st.text_input("Tu consulta")
    # st.button devuelve True solo en la ejecución que provocó el clic en el botón.
    if st.button("Enviar"):
        if not question.strip():
            st.warning("El mensaje no puede estar vacío.")
        else:
            # Una conversación nueva en cada consulta: hoy la web no tiene memoria (eso, en la Clase 9).
            messages = [
                {"role": "system", "content": build_system_prompt()},
                {"role": "user", "content": question},
            ]
            try:
                # Mientras el agente trabaja, la página muestra un aviso de espera.
                with st.spinner(f"{ASSISTANT_NAME} está pensando..."):
                    answer = run_agent(messages)
                # Streamlit lee el texto como Markdown: lo que queda entre dos signos $ se dibuja como
                # fórmula matemática ("$8.000 por día ... $16.000" sale ilegible). Con \$ el signo se ve tal cual.
                st.success(answer.replace("$", "\\$"))
            except (ValueError, ConnectionError, MissingAPIKeyError) as error:
                st.error(f"Error controlado: {error}")

with marta_tab:
    st.write(f"Para Marta: {ASSISTANT_NAME} clasifica las consultas de {QUERIES_FILE} y prepara un borrador de respuesta.")
    # Cada clic procesa el archivo de nuevo: gasta unos 3.300 tokens (7 llamadas al modelo).
    if st.button("Procesar las consultas del día"):
        try:
            with st.spinner("Procesando las consultas..."):
                results, metadata = run_pipeline(load_queries(QUERIES_FILE))
            # Si algo falla antes de esta línea, show_report no se ejecuta y se muestra el error.
            show_report(results, metadata)
        except (OSError, ValueError, MissingAPIKeyError) as error:
            # El mismo error controlado de siempre, ahora en un recuadro rojo de la página.
            st.error(f"Error controlado: {error}")
