ASSISTANT_NAME = "Rayo"

FAQ = {
    "horario": "Abrimos de lunes a viernes de 9 a 13 y de 16 a 20, y los sábados de 9 a 13.",
    "dirección": "Estamos en Av. del Sur 1234.",
    "service": "El service básico cuesta $25.000 y el completo $45.000.",
    "demora": "El taller entrega las bicicletas en 48 horas hábiles.",
    "alquiler": "Alquilamos bicicletas urbanas a $8.000 por día.",
}


def get_user_input():
    """Pide un mensaje por consola y lo devuelve."""
    return input("Tú: ")


def call_ai_model(prompt):
    """Simula al modelo de lenguaje: busca una palabra clave del FAQ en el mensaje."""
    text = prompt.strip().lower()
    if not text:
        raise ValueError("el mensaje no puede estar vacío.")
    for keyword, answer in FAQ.items():
        if keyword in text:
            return answer
    return "Todavía no sé responder eso. Se lo paso a Marta."


def main():
    print(f"Hola, soy {ASSISTANT_NAME}, el asistente de Rodados Sur.")
    print("Escribe 'salir' para terminar.")
    history = []
    while True:
        message = get_user_input()
        if message.strip().lower() == "salir":
            break
        answer = call_ai_model(message)
        history.append(message)
        print(f"{ASSISTANT_NAME}: {answer}")
    print(f"{ASSISTANT_NAME}: ¡Hasta luego! Consultas respondidas hoy: {len(history)}.")


if __name__ == "__main__":
    main()
