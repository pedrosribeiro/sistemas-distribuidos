import base64
import json

import pika
from app.shared.config import RABBITMQ_HOST, RABBITMQ_PASS, RABBITMQ_USER


def publish_result(resultado, assinatura, aprovado):
    connection = pika.BlockingConnection(
        pika.ConnectionParameters(
            RABBITMQ_HOST,
            credentials=pika.PlainCredentials(RABBITMQ_USER, RABBITMQ_PASS),
        )
    )
    channel = connection.channel()

    fila = "pagamento-aprovado" if aprovado else "pagamento-recusado"
    channel.queue_declare(queue=fila)

    mensagem = {
        "resultado": resultado,
        "assinatura": base64.b64encode(assinatura).decode(),
    }

    channel.basic_publish(exchange="", routing_key=fila, body=json.dumps(mensagem))
    print(f"[MS Pagamento] Publicado em {fila}: {resultado}")
    connection.close()
