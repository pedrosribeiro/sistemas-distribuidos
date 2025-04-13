import json

import pika

from app.ms_pagamento.service import process_payment
from app.shared.config import RABBITMQ_HOST, RABBITMQ_PASS, RABBITMQ_USER


def start_consuming():
    connection = pika.BlockingConnection(
        pika.ConnectionParameters(
            RABBITMQ_HOST,
            credentials=pika.PlainCredentials(RABBITMQ_USER, RABBITMQ_PASS),
        )
    )
    channel = connection.channel()

    channel.queue_declare(queue="reserva-criada")

    def callback(ch, method, properties, body):
        data = json.loads(body)
        print(f"[MS Pagamento] Reserva recebida: {data}")
        process_payment(data)

    channel.basic_consume(
        queue="reserva-criada", on_message_callback=callback, auto_ack=True
    )
    print("[MS Pagamento] Aguardando reservas...")
    channel.start_consuming()
