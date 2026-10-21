import json
import logging
import os

import streamlit as st

from assistant import ASSISTANT_NAME, FAQ, build_system_prompt, run_agent
from llm_client import MissingAPIKeyError
from pipeline import QUERIES_FILE, count_by, load_queries, run_pipeline
from tools import HANDOFFS_FILE, hand_off_to_marta

RESULT_COLUMNS = ("id", "canal", "estado", "mensaje", "respuesta", "detalle")
HANDOFF_COLUMNS = ("fecha", "urgencia", "contacto", "motivo")
FALLBACK_ANSWER = f"En este momento no puedo responder, pero dejé tu consulta para Marta. {FAQ['dirección']} {FAQ['horario']}"


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


def show_handoffs():
    """Muestra las consultas que Rayo le derivó a Marta: cuántas de cada urgencia y la lista, de la más nueva a la más vieja."""
    try:
        with open(HANDOFFS_FILE, encoding="utf-8") as file:
            handoffs = json.load(file)
    except FileNotFoundError:
        st.info("Todavía no hay consultas derivadas.")
        return
    counts = count_by(handoffs, "urgencia")
    col1, col2, col3 = st.columns(3)
    col1.metric("Urgencia alta", counts.get("alta", 0))
    col2.metric("Urgencia media", counts.get("media", 0))
    col3.metric("Urgencia baja", counts.get("baja", 0))
    st.dataframe(list(reversed(handoffs)), column_order=HANDOFF_COLUMNS, hide_index=True)


def start_conversation():
    """Empieza una conversación nueva: la memoria solo con las instrucciones del agente."""
    st.session_state.messages = [{"role": "system", "content": build_system_prompt()}]


def show_message(role, text):
    """Dibuja un mensaje del chat: el del cliente o el de Rayo."""
    with st.chat_message(role):
        st.markdown(text.replace("$", "\\$"))


def show_history(messages):
    """Muestra la conversación: solo lo que escribió el cliente y lo que respondió Rayo."""
    for message in messages:
        if message["role"] == "user":
            show_message("user", message["content"])
        elif message["role"] == "assistant" and message.get("content") and not message.get("tool_calls"):
            show_message("assistant", message["content"])


def answer_question(messages, question):
    """Rayo responde. Si algo falla, la consulta no se pierde: respuesta alternativa, registro y derivación a Marta."""
    start = len(messages)
    messages.append({"role": "user", "content": question})
    try:
        return run_agent(messages)
    except (ValueError, ConnectionError, MissingAPIKeyError) as error:
        del messages[start + 1:]
        messages.append({"role": "assistant", "content": FALLBACK_ANSWER})
        logging.warning(f"Chat: {ASSISTANT_NAME} no pudo responder y la consulta pasó a Marta. Motivo: {error}")
        hand_off_to_marta(f"{ASSISTANT_NAME} no pudo responder: {question}", "media", "sin datos")
        return FALLBACK_ANSWER


st.set_page_config(page_title="Rodados Sur", layout="wide")
st.title(f"{ASSISTANT_NAME}, el asistente de Rodados Sur")
if "messages" not in st.session_state:
    start_conversation()
client_tab, marta_tab = st.tabs([f"Chatear con {ASSISTANT_NAME}", "Panel de Marta"])

with client_tab:
    st.write("Pregunta por horarios, precios, el estado de tu orden o el clima para salir en bici.")
    if st.button("Nueva conversación"):
        start_conversation()
    messages = st.session_state.messages
    chat = st.container(height=420)
    with chat:
        show_history(messages)
    question = st.chat_input("Escribe tu consulta", max_chars=500)
    if question:
        with chat:
            show_message("user", question)
            with st.spinner(f"{ASSISTANT_NAME} está pensando..."):
                answer = answer_question(messages, question)
            show_message("assistant", answer)
    st.caption(f"Mensajes en la memoria de {ASSISTANT_NAME}: {len(messages)}")

with marta_tab:
    password = st.text_input("Clave de Marta", type="password")
    if not password:
        st.info("Esta sección es solo para Marta: escribe la clave.")
    elif password != os.getenv("MARTA_PASSWORD"):
        st.error("La clave no es correcta.")
    else:
        st.subheader("Consultas derivadas")
        show_handoffs()
        st.subheader("Consultas del día")
        st.write(f"{ASSISTANT_NAME} clasifica las consultas de {QUERIES_FILE} y prepara un borrador de respuesta.")
        if st.button("Procesar las consultas del día"):
            try:
                with st.spinner("Procesando las consultas..."):
                    results, metadata = run_pipeline(load_queries(QUERIES_FILE))
                show_report(results, metadata)
            except (OSError, ValueError, MissingAPIKeyError) as error:
                st.error(f"Error controlado: {error}")
