import json

import pika

from app.shared.config import RABBITMQ_HOST, RABBITMQ_PASS, RABBITMQ_USER


def processar_promocao(ch, method, properties, body):
    data = json.loads(body)
    print(f"\n[PROMOÇÃO RECEBIDA]")
    print(f"Destino: {data.get('destino')}")
    print(f"Mensagem: {data.get('mensagem')}")
    print(f"Válida até: {data.get('valido_ate')}\n")


def start_consuming(destino):
    nome_fila = f"promocoes-destino_{destino.lower().replace(' ', '_')}"

    connection = pika.BlockingConnection(
        pika.ConnectionParameters(
            host=RABBITMQ_HOST,
            credentials=pika.PlainCredentials(RABBITMQ_USER, RABBITMQ_PASS),
        )
    )
    channel = connection.channel()
    channel.queue_declare(queue=nome_fila)

    channel.basic_consume(
        queue=nome_fila, on_message_callback=processar_promocao, auto_ack=True
    )

    print(f"[SUBSCRIBER PROMOÇÕES] Aguardando promoções para {destino}...\n")
    channel.start_consuming()
