import json
import logging

import pika
from app.shared.config import RABBITMQ_HOST, RABBITMQ_PASS, RABBITMQ_USER

def publicar_reserva(reserva):
    connection = pika.BlockingConnection(
        pika.ConnectionParameters(
            host=RABBITMQ_HOST,
            credentials=pika.PlainCredentials(RABBITMQ_USER, RABBITMQ_PASS),
        )
    )
    channel = connection.channel()
    channel.queue_declare(queue="reserva-criada")

    channel.basic_publish(
        exchange="", routing_key="reserva-criada", body=json.dumps(reserva)
    )
    connection.close()
