import base64
import json

import pika

from app.ms_bilhete.publisher import publicar_bilhete
from app.shared.config import RABBITMQ_HOST, RABBITMQ_PASS, RABBITMQ_USER
from app.shared.crypto_utils import load_public_key, verify_signature

KEY_PATH = "app/ms_pagamento/keys/public_key.pem"
public_key = load_public_key(KEY_PATH)


def processar_pagamento_aprovado(ch, method, properties, body):
    data = json.loads(body)
    resultado = data.get("resultado")
    assinatura = base64.b64decode(data.get("assinatura"))

    mensagem_bytes = json.dumps(resultado).encode()

    if verify_signature(mensagem_bytes, assinatura, public_key):
        print(
            f"[MS BILHETE] Assinatura VERIFICADA para reserva {resultado['reserva_id']}"
        )

        bilhete = {
            "reserva_id": resultado["reserva_id"],
            "codigo_bilhete": f"BILHETE-{resultado['reserva_id'][:8]}",
            "confirmado_em": resultado.get("data_pagamento", "2025-04-13"),
        }

        publicar_bilhete(bilhete)

    else:
        print("[MS BILHETE] Assinatura INVÁLIDA — mensagem ignorada")


def start_consuming():
    print(f"Conectando ao RabbitMQ em {RABBITMQ_HOST} com usuário {RABBITMQ_USER}...")
    connection = pika.BlockingConnection(
        pika.ConnectionParameters(
            host=RABBITMQ_HOST,
            credentials=pika.PlainCredentials(RABBITMQ_USER, RABBITMQ_PASS),
        )
    )
    channel = connection.channel()

    channel.queue_declare(queue="pagamento-aprovado")
    channel.basic_consume(
        queue="pagamento-aprovado",
        on_message_callback=processar_pagamento_aprovado,
        auto_ack=True,
    )

    print("[MS BILHETE] Aguardando pagamentos aprovados...")
    channel.start_consuming()
