import base64
import json
import logging

import pika
from app.ms_bilhete.publisher import publicar_bilhete
from app.shared.config import RABBITMQ_HOST, RABBITMQ_PASS, RABBITMQ_USER

from datetime import datetime

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s",
    handlers=[logging.StreamHandler()],
)


def processar_pagamento_aprovado(ch, method, properties, body):
    data = json.loads(body)

    reserva_id = data.get("reserva_id")

    bilhete = {
        "reserva_id": reserva_id,
        "codigo_bilhete": f"BILHETE-{reserva_id[:8]}",
        "confirmado_em": datetime.now().isoformat()
    }

    publicar_bilhete(bilhete)


def start_consuming():
    connection = pika.BlockingConnection(
        pika.ConnectionParameters(
            host=RABBITMQ_HOST,
            credentials=pika.PlainCredentials(RABBITMQ_USER, RABBITMQ_PASS),
        )
    )
    channel = connection.channel()

    # Declara a exchange do tipo fanout
    channel.exchange_declare(
        exchange="pagamento-aprovado-exchange", exchange_type="fanout"
    )

    # Cria uma fila exclusiva para este consumidor e faz o bind na exchange
    result = channel.queue_declare(queue="", exclusive=True)
    queue_name = result.method.queue
    channel.queue_bind(exchange="pagamento-aprovado-exchange", queue=queue_name)

    channel.basic_consume(
        queue=queue_name,
        on_message_callback=processar_pagamento_aprovado,
        auto_ack=True,
    )

    logging.info(
        "[MS BILHETE] Aguardando pagamentos aprovados (via exchange fanout)..."
    )
    channel.start_consuming()
