ASSISTANT_NAME = "Rayo"

FAQ = {
    "horario": "Abrimos de lunes a viernes de 9 a 13 y de 16 a 20, y los sábados de 9 a 13.",
    "dirección": "Estamos en Av. del Sur 1234.",
    "service": "El service básico cuesta $25.000 y el completo $45.000.",
    "demora": "El taller entrega las bicicletas en 48 horas hábiles.",
}

history = []

print(f"Hola, soy {ASSISTANT_NAME}, el asistente de Rodados Sur.")
print("Escribe 'salir' para terminar.")

while True:
    message = input("Tú: ")
    if message.lower() == "salir":
        break
    answer = "Todavía no sé responder eso. Se lo paso a Marta."
    for keyword, text in FAQ.items():
        if keyword in message.lower():
            answer = text
    history.append(message)
    print(f"{ASSISTANT_NAME}: {answer}")

print(f"{ASSISTANT_NAME}: ¡Hasta luego! Consultas respondidas hoy: {len(history)}.")
