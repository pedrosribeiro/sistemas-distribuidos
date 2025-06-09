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

    # Declare a fanout exchange
    exchange_name = "promocoes_exchange"
    channel.exchange_declare(exchange=exchange_name, exchange_type="direct")

    channel.basic_publish(
        exchange=exchange_name,
        routing_key=promocao["destino"],
        body=json.dumps(promocao),
    )

    logging.info(f"[MS MARKETING] Promoção publicada na exchange: {exchange_name}")
    connection.close()
