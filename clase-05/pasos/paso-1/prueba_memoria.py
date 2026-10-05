from llm_client import chat_completion

SYSTEM = {"role": "system", "content": "Eres Rayo, el asistente de Rodados Sur. Responde en una oración."}

print("--- Sin memoria: cada consulta viaja sola ---")
first = [SYSTEM, {"role": "user", "content": "Hola, me llamo Ana y dejé mi bici en el taller."}]
print(chat_completion(first)["content"])
second = [SYSTEM, {"role": "user", "content": "¿Cómo me llamo?"}]
print(chat_completion(second)["content"])

print("--- Con memoria: enviamos toda la conversación ---")
messages = [SYSTEM, {"role": "user", "content": "Hola, me llamo Ana y dejé mi bici en el taller."}]
answer = chat_completion(messages)
messages.append({"role": "assistant", "content": answer["content"]})
print(answer["content"])
messages.append({"role": "user", "content": "¿Cómo me llamo?"})
print(chat_completion(messages)["content"])
print(f"Mensajes enviados en la última llamada: {len(messages)}")
