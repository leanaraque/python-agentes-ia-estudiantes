import json

import streamlit as st

from assistant import ASSISTANT_NAME, build_system_prompt, run_agent
from llm_client import MissingAPIKeyError
from pipeline import QUERIES_FILE, load_queries, run_pipeline

RESULT_COLUMNS = ("id", "canal", "estado", "mensaje", "respuesta", "detalle")


def show_report(results, metadata):
    """Muestra el reporte del pipeline: los números del día, la tabla y el botón para descargarlo."""
    counts = metadata["por_estado"]
    col1, col2, col3, col4 = st.columns(4)
    col1.metric("Listas", counts.get("lista", 0))
    col2.metric("Para Marta", counts.get("para Marta", 0))
    col3.metric("Inválidas", counts.get("inválida", 0))
    col4.metric("Con error", counts.get("error", 0))
    st.caption(f"{metadata['total']} consultas en {metadata['segundos']} s. Reporte guardado en {metadata['carpeta']}")
    st.dataframe(results, column_order=RESULT_COLUMNS, hide_index=True)
    report = json.dumps(results, ensure_ascii=False, indent=2)
    st.download_button("Descargar resultados (JSON)", report, file_name="resultados.json")


st.set_page_config(page_title="Rodados Sur", layout="wide")
st.title(f"{ASSISTANT_NAME}, el asistente de Rodados Sur")
client_tab, marta_tab = st.tabs([f"Preguntar a {ASSISTANT_NAME}", "Consultas del día"])

with client_tab:
    st.write("Pregunta por horarios, precios, el estado de tu orden o el clima para salir en bici.")
    question = st.text_input("Tu consulta")
    if st.button("Enviar"):
        if not question.strip():
            st.warning("El mensaje no puede estar vacío.")
        else:
            messages = [
                {"role": "system", "content": build_system_prompt()},
                {"role": "user", "content": question},
            ]
            try:
                with st.spinner(f"{ASSISTANT_NAME} está pensando..."):
                    answer = run_agent(messages)
                st.success(answer.replace("$", "\\$"))
            except (ValueError, ConnectionError, MissingAPIKeyError) as error:
                st.error(f"Error controlado: {error}")

with marta_tab:
    st.write(f"Para Marta: {ASSISTANT_NAME} clasifica las consultas de {QUERIES_FILE} y prepara un borrador de respuesta.")
    if st.button("Procesar las consultas del día"):
        try:
            with st.spinner("Procesando las consultas..."):
                results, metadata = run_pipeline(load_queries(QUERIES_FILE))
            show_report(results, metadata)
        except (OSError, ValueError, MissingAPIKeyError) as error:
            st.error(f"Error controlado: {error}")
