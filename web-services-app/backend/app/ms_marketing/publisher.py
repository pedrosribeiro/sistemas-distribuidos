import json
import logging

import pika
from app.shared.config import RABBITMQ_HOST, RABBITMQ_PASS, RABBITMQ_USER

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s",
    handlers=[logging.StreamHandler()],
)


def publicar_promocao(promocao: dict):
    connection = pika.BlockingConnection(
        pika.ConnectionParameters(
            host=RABBITMQ_HOST,
            credentials=pika.PlainCredentials(RABBITMQ_USER, RABBITMQ_PASS),
        )
    )
    channel = connection.channel()

    # Declare a normal queue
    queue_name = "promocoes"
    channel.queue_declare(queue=queue_name, durable=False)

    channel.basic_publish(
        exchange='',
        routing_key=queue_name,
        body=json.dumps(promocao),
    )

    logging.info(f"[MS MARKETING] Promoção publicada na fila: {queue_name}")
    connection.close()
