import json
import logging

import pika
from app.shared.config import RABBITMQ_HOST, RABBITMQ_PASS, RABBITMQ_USER

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s",
    handlers=[logging.StreamHandler()],
)


def publicar_bilhete(bilhete):
    connection = pika.BlockingConnection(
        pika.ConnectionParameters(
            host=RABBITMQ_HOST,
            credentials=pika.PlainCredentials(RABBITMQ_USER, RABBITMQ_PASS),
        )
    )
    channel = connection.channel()
    channel.queue_declare(queue="bilhete-gerado")

    channel.basic_publish(
        exchange="", routing_key="bilhete-gerado", body=json.dumps(bilhete)
    )

    logging.info(
        f"[MS BILHETE] Bilhete gerado e publicado: {bilhete['codigo_bilhete']}"
    )
    connection.close()
