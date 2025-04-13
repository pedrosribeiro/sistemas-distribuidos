import json

import pika

from app.shared.config import RABBITMQ_HOST, RABBITMQ_PASS, RABBITMQ_USER


def publicar_promocao(promocao: dict):
    destino = promocao.get("destino", "").lower().replace(" ", "_")
    nome_fila = f"promocoes-destino_{destino}"

    connection = pika.BlockingConnection(
        pika.ConnectionParameters(
            host=RABBITMQ_HOST,
            credentials=pika.PlainCredentials(RABBITMQ_USER, RABBITMQ_PASS),
        )
    )
    channel = connection.channel()
    channel.queue_declare(queue=nome_fila)

    channel.basic_publish(exchange="", routing_key=nome_fila, body=json.dumps(promocao))

    print(f"[MS MARKETING] Promoção publicada na fila: {nome_fila}")
    connection.close()
