# app.py, paso 3: el soporte con control humano.
# La segunda pestaña es el panel de Marta, protegido con una clave (MARTA_PASSWORD del .env):
# las consultas que Rayo le derivó (con el contacto del cliente) y las consultas del día.
import json
# logging: el registro de la Clase 8. Lo configura pipeline.py (al importarlo), así que
# las líneas del chat van a la terminal y a pipeline.log.
import logging
# os: para leer MARTA_PASSWORD con os.getenv (el .env ya lo cargó assistant.py al importarlo).
import os

# Streamlit convierte un programa de Python en una página web, sin escribir HTML.
import streamlit as st

# Del agente también importamos el FAQ (Clase 1): la respuesta alternativa sale de ahí, sin modelo.
from assistant import ASSISTANT_NAME, FAQ, build_system_prompt, run_agent
from llm_client import MissingAPIKeyError
# count_by (Clase 8) cuenta cuántas hay de cada valor: hoy, cuántas derivaciones de cada urgencia.
from pipeline import QUERIES_FILE, count_by, load_queries, run_pipeline
# HANDOFFS_FILE es "derivaciones.json": el panel de Marta lee ese archivo.
from tools import HANDOFFS_FILE, hand_off_to_marta

RESULT_COLUMNS = ("id", "canal", "estado", "mensaje", "respuesta", "detalle")
# Las columnas de la tabla de derivaciones, en este orden.
HANDOFF_COLUMNS = ("fecha", "urgencia", "contacto", "motivo")
# La respuesta alternativa: no necesita al modelo. Se arma con el FAQ, como las reglas de la Clase 1.
FALLBACK_ANSWER = f"En este momento no puedo responder, pero dejé tu consulta para Marta. {FAQ['dirección']} {FAQ['horario']}"


# El reporte del pipeline, igual que en la Clase 8.
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


# Nueva: lo que Rayo le pasó a Marta. Es el "control humano" del sistema de soporte.
def show_handoffs():
    """Muestra las consultas que Rayo le derivó a Marta: cuántas de cada urgencia y la lista, de la más nueva a la más vieja."""
    try:
        with open(HANDOFFS_FILE, encoding="utf-8") as file:
            handoffs = json.load(file)
    # Si todavía nadie fue derivado, el archivo no existe: lo decimos en lugar de mostrar un error.
    except FileNotFoundError:
        st.info("Todavía no hay consultas derivadas.")
        # return sin valor: termina la función acá (no hay nada más que mostrar).
        return
    counts = count_by(handoffs, "urgencia")
    # Tres números grandes: cuántas de urgencia alta, media y baja.
    col1, col2, col3 = st.columns(3)
    col1.metric("Urgencia alta", counts.get("alta", 0))
    col2.metric("Urgencia media", counts.get("media", 0))
    col3.metric("Urgencia baja", counts.get("baja", 0))
    # reversed da la lista al revés: la derivación más nueva queda arriba.
    st.dataframe(list(reversed(handoffs)), column_order=HANDOFF_COLUMNS, hide_index=True)


# st.session_state es un diccionario que Streamlit CONSERVA entre ejecuciones del archivo
# (y uno distinto para cada persona que abre la página). Ahí guardamos la memoria.
def start_conversation():
    """Empieza una conversación nueva: la memoria solo con las instrucciones del agente."""
    st.session_state.messages = [{"role": "system", "content": build_system_prompt()}]


# role "user" o "assistant": st.chat_message dibuja la burbuja con el ícono de cada uno.
def show_message(role, text):
    """Dibuja un mensaje del chat: el del cliente o el de Rayo."""
    with st.chat_message(role):
        # El arreglo del signo $ de la Clase 8: sin esto, el texto entre dos $ se dibuja como fórmula.
        st.markdown(text.replace("$", "\\$"))


# En cada clic, Streamlit borra la página y la vuelve a dibujar: hay que mostrar de nuevo
# toda la conversación guardada.
def show_history(messages):
    """Muestra la conversación: solo lo que escribió el cliente y lo que respondió Rayo."""
    for message in messages:
        if message["role"] == "user":
            show_message("user", message["content"])
        # En la memoria también están las instrucciones (system), los pedidos de herramientas y sus
        # resultados (tool): el cliente no tiene por qué verlos. Solo mostramos las respuestas con texto.
        elif message["role"] == "assistant" and message.get("content") and not message.get("tool_calls"):
            show_message("assistant", message["content"])


# Nueva: el control de flujo del chat. Camino normal: Rayo responde.
# Camino alternativo: algo falló y la consulta igual queda atendida.
def answer_question(messages, question):
    """Rayo responde. Si algo falla, la consulta no se pierde: respuesta alternativa, registro y derivación a Marta."""
    start = len(messages)
    messages.append({"role": "user", "content": question})
    try:
        return run_agent(messages)
    except (ValueError, ConnectionError, MissingAPIKeyError) as error:
        # Borramos lo que haya quedado a medias de este turno (por ejemplo, un pedido de herramienta sin
        # respuesta), pero dejamos la pregunta del cliente: start es su posición y start + 1, lo que sigue.
        del messages[start + 1:]
        # La respuesta alternativa queda en la memoria: la conversación sigue teniendo sentido.
        messages.append({"role": "assistant", "content": FALLBACK_ANSWER})
        # El detalle técnico va al registro (para quien mantiene la app), no a la pantalla del cliente.
        logging.warning(f"Chat: {ASSISTANT_NAME} no pudo responder y la consulta pasó a Marta. Motivo: {error}")
        # La decisión la toma Python, no el modelo (que justo falló). Sin datos de contacto:
        # Marta ve qué preguntaron y que Rayo no pudo responder.
        hand_off_to_marta(f"{ASSISTANT_NAME} no pudo responder: {question}", "media", "sin datos")
        return FALLBACK_ANSWER


st.set_page_config(page_title="Rodados Sur", layout="wide")
# IMPORTANTE: Streamlit ejecuta este archivo de arriba a abajo cada vez que alguien toca algo.
st.title(f"{ASSISTANT_NAME}, el asistente de Rodados Sur")
# Solo la PRIMERA vez (cuando la persona abre la página) se crea la memoria. En las siguientes
# ejecuciones ya existe y no se toca: por eso Rayo recuerda.
if "messages" not in st.session_state:
    start_conversation()
# La segunda pestaña ahora es el panel de Marta: derivaciones y consultas del día.
client_tab, marta_tab = st.tabs([f"Chatear con {ASSISTANT_NAME}", "Panel de Marta"])

with client_tab:
    st.write("Pregunta por horarios, precios, el estado de tu orden o el clima para salir en bici.")
    # Empieza de cero: útil para probar, y para que la memoria (y los tokens) no crezcan sin fin.
    if st.button("Nueva conversación"):
        start_conversation()
    # messages es la MISMA lista guardada (no una copia): lo que run_agent le agrega queda guardado.
    messages = st.session_state.messages
    # Un recuadro de altura fija con barra de desplazamiento, como en las apps de mensajes.
    chat = st.container(height=420)
    with chat:
        show_history(messages)
    # La caja de chat: devuelve el texto cuando la persona presiona Enter (si no, None).
    # Valida sola: no envía mensajes vacíos y max_chars corta en 500 caracteres.
    question = st.chat_input("Escribe tu consulta", max_chars=500)
    # Solo en la ejecución en la que llegó un mensaje nuevo.
    if question:
        with chat:
            show_message("user", question)
            # Mientras el agente trabaja, la página muestra un aviso de espera.
            with st.spinner(f"{ASSISTANT_NAME} está pensando..."):
                answer = answer_question(messages, question)
            show_message("assistant", answer)
    # Cuántos mensajes viajan al modelo en la próxima consulta. Cada pregunta suma al menos dos
    # (la pregunta y la respuesta), y más si usó herramientas: la memoria cuesta tokens.
    st.caption(f"Mensajes en la memoria de {ASSISTANT_NAME}: {len(messages)}")

with marta_tab:
    # type="password": lo que se escribe se ve como puntos.
    password = st.text_input("Clave de Marta", type="password")
    if not password:
        st.info("Esta sección es solo para Marta: escribe la clave.")
    # La clave correcta está en el .env (en la nube, en Secrets), nunca en el código.
    # Si MARTA_PASSWORD no existe, os.getenv devuelve None y ninguna clave sirve: queda cerrado.
    elif password != os.getenv("MARTA_PASSWORD"):
        st.error("La clave no es correcta.")
    else:
        st.subheader("Consultas derivadas")
        show_handoffs()
        st.subheader("Consultas del día")
        st.write(f"{ASSISTANT_NAME} clasifica las consultas de {QUERIES_FILE} y prepara un borrador de respuesta.")
        # Detrás de la clave: en la Clase 8 cualquiera con el link podía gastar tokens con este botón.
        if st.button("Procesar las consultas del día"):
            try:
                with st.spinner("Procesando las consultas..."):
                    results, metadata = run_pipeline(load_queries(QUERIES_FILE))
                show_report(results, metadata)
            except (OSError, ValueError, MissingAPIKeyError) as error:
                # El cliente ve el error técnico en rojo. En el paso 2 esto se mejora.
                st.error(f"Error controlado: {error}")
