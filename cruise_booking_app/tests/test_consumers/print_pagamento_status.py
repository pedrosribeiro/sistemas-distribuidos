import base64
import json

import pika

from app.shared.config import RABBITMQ_HOST, RABBITMQ_PASS, RABBITMQ_USER
from app.shared.crypto_utils import load_public_key, verify_signature

# Carrega a chave pública do ms_pagamento
public_key = load_public_key("app/ms_pagamento/keys/public_key.pem")


def process_mensagem(ch, method, properties, body):
    data = json.loads(body)
    resultado = data.get("resultado")
    assinatura_b64 = data.get("assinatura")

    mensagem_bytes = json.dumps(resultado).encode()
    assinatura = base64.b64decode(assinatura_b64)

    status = resultado.get("status")
    fila = method.routing_key
    print(f"\n[TESTE CONSUMIDOR] Mensagem recebida da fila {fila}:")
    print(json.dumps(resultado, indent=2))

    if verify_signature(mensagem_bytes, assinatura, public_key):
        print("Assinatura VERIFICADA com sucesso!\n")
    else:
        print("Assinatura INVÁLIDA!\n")


def start_consuming():
    connection = pika.BlockingConnection(
        pika.ConnectionParameters(
            host=RABBITMQ_HOST,
            credentials=pika.PlainCredentials(RABBITMQ_USER, RABBITMQ_PASS),
        )
    )
    channel = connection.channel()

    channel.queue_declare(queue="pagamento-aprovado")
    channel.queue_declare(queue="pagamento-recusado")

    channel.basic_consume(
        queue="pagamento-aprovado", on_message_callback=process_mensagem, auto_ack=True
    )
    channel.basic_consume(
        queue="pagamento-recusado", on_message_callback=process_mensagem, auto_ack=True
    )

    print("[TESTE CONSUMIDOR] Aguardando mensagens de pagamento...")
    channel.start_consuming()


if __name__ == "__main__":
    start_consuming()
