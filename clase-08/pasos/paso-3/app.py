import streamlit as st

from assistant import ASSISTANT_NAME, build_system_prompt, run_agent
from llm_client import MissingAPIKeyError

st.set_page_config(page_title="Rodados Sur")
st.title(f"{ASSISTANT_NAME}, el asistente de Rodados Sur")
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
