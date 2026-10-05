from llm_client import chat_completion
from tools import TOOLS, execute_tool

messages = [
    {"role": "system", "content": "Eres Rayo, el asistente de Rodados Sur. Usa las herramientas cuando haga falta. Responde en español, en una o dos oraciones."},
    {"role": "user", "content": "Hola, ¿cómo va mi orden 1043?"},
]

message = chat_completion(messages, tools=TOOLS)
print("1. El modelo pide:", message.get("tool_calls"))

call = message["tool_calls"][0]
result = execute_tool(call["function"]["name"], call["function"]["arguments"])
print("2. Resultado de la herramienta:", result)

messages.append(message)
messages.append({"role": "tool", "tool_call_id": call["id"], "content": result})
final = chat_completion(messages, tools=TOOLS)
print("3. Respuesta final:", final["content"])
