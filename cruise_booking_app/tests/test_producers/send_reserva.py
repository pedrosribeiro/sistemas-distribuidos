import json
import uuid

import pika

from app.shared.config import RABBITMQ_HOST, RABBITMQ_PASS, RABBITMQ_USER


def send_test_reserva():
    connection = pika.BlockingConnection(
        pika.ConnectionParameters(
            host=RABBITMQ_HOST,
            credentials=pika.PlainCredentials(RABBITMQ_USER, RABBITMQ_PASS),
        )
    )
    channel = connection.channel()
    channel.queue_declare(queue="reserva-criada")

    reserva = {
        "reserva_id": str(uuid.uuid4()),
        "cliente": "Pedro Teste",
        "destino": "Caribe",
        "data_embarque": "2025-07-13",
        "num_passageiros": 2,
        "num_cabines": 1,
        "valor": 4999.90,
    }

    channel.basic_publish(
        exchange="", routing_key="reserva-criada", body=json.dumps(reserva)
    )

    print(f"[TESTE] Reserva enviada para a fila: {reserva['reserva_id']}")
    connection.close()


if __name__ == "__main__":
    send_test_reserva()
