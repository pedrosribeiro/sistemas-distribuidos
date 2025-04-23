import base64
import json
import logging

import pika
from app.shared.config import RABBITMQ_HOST, RABBITMQ_PASS, RABBITMQ_USER

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s",
    handlers=[logging.StreamHandler()],
)


def publish_result(resultado, assinatura, aprovado):
    connection = pika.BlockingConnection(
        pika.ConnectionParameters(
            RABBITMQ_HOST,
            credentials=pika.PlainCredentials(RABBITMQ_USER, RABBITMQ_PASS),
        )
    )
    channel = connection.channel()

    mensagem = {
        "resultado": resultado,
        "assinatura": base64.b64encode(assinatura).decode(),
    }

    if aprovado:
        # Declara a exchange do tipo fanout
        channel.exchange_declare(
            exchange="pagamento-aprovado-exchange", exchange_type="fanout"
        )

        # Cria uma fila exclusiva para este consumidor e faz o bind na exchange
        result = channel.queue_declare(queue="", exclusive=True)
        queue_name = result.method.queue
        channel.queue_bind(exchange="pagamento-aprovado-exchange", queue=queue_name)

        channel.basic_publish(
            exchange="pagamento-aprovado-exchange",
            routing_key="",
            body=json.dumps(mensagem),
        )

        logging.info(
            f"[MS Pagamento] Publicado em pagamento-aprovado-exchange: {resultado}"
        )
    else:
        channel.queue_declare(queue="pagamento-recusado")

        channel.basic_publish(
            exchange="", routing_key="pagamento-recusado", body=json.dumps(mensagem)
        )
        logging.info(f"[MS Pagamento] Publicado em pagamento-recusado: {resultado}")

    connection.close()
