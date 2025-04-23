import base64
import json
import logging

import pika
from app.ms_bilhete.publisher import publicar_bilhete
from app.shared.config import RABBITMQ_HOST, RABBITMQ_PASS, RABBITMQ_USER
from app.shared.crypto_utils import load_public_key, verify_signature

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s",
    handlers=[logging.StreamHandler()],
)

KEY_PATH = "app/ms_bilhete/keys/public_key.pem"
public_key = load_public_key(KEY_PATH)


def processar_pagamento_aprovado(ch, method, properties, body):
    data = json.loads(body)
    resultado = data.get("resultado")
    assinatura = base64.b64decode(data.get("assinatura"))

    mensagem_bytes = json.dumps(resultado).encode()

    if verify_signature(mensagem_bytes, assinatura, public_key):
        logging.info(
            f"[MS BILHETE] Assinatura VERIFICADA para reserva {resultado['reserva_id']}"
        )

        bilhete = {
            "reserva_id": resultado["reserva_id"],
            "codigo_bilhete": f"BILHETE-{resultado['reserva_id'][:8]}",
            "confirmado_em": resultado.get("data_pagamento", "2025-04-13"),
        }

        publicar_bilhete(bilhete)

    else:
        logging.info("[MS BILHETE] Assinatura INVÁLIDA — mensagem ignorada")


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
