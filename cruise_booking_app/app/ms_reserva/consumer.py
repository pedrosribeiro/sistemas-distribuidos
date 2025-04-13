import base64
import json
from pathlib import Path

import pika

from app.shared.config import RABBITMQ_HOST, RABBITMQ_PASS, RABBITMQ_USER
from app.shared.crypto_utils import load_public_key, verify_signature

RESERVAS_PATH = Path("app/ms_reserva/data/reservas.json")
KEY_PATH = "app/ms_pagamento/keys/public_key.pem"
public_key_pagamento = load_public_key(KEY_PATH)


def atualizar_reserva_status(reserva_id, novo_status):
    if not RESERVAS_PATH.exists():
        print(f"[MS RESERVA] Arquivo de reservas não encontrado.")
        return

    with open(RESERVAS_PATH, "r", encoding="utf-8") as f:
        reservas = json.load(f)

    for r in reservas:
        if r["reserva_id"] == reserva_id:
            r["status"] = novo_status
            break

    with open(RESERVAS_PATH, "w", encoding="utf-8") as f:
        json.dump(reservas, f, indent=2)

    print(
        f"[MS RESERVA] Status atualizado para '{novo_status}' (reserva_id: {reserva_id})"
    )


def processar_pagamento(ch, method, properties, body):
    fila = method.routing_key
    data = json.loads(body)

    resultado = data.get("resultado")
    assinatura = base64.b64decode(data.get("assinatura"))

    mensagem_bytes = json.dumps(resultado).encode()

    if verify_signature(mensagem_bytes, assinatura, public_key_pagamento):
        print(f"[MS RESERVA] Assinatura VERIFICADA de '{fila}'")
        status = resultado["status"]
        atualizar_reserva_status(resultado["reserva_id"], status)
    else:
        print(f"[MS RESERVA] Assinatura INVÁLIDA recebida na fila '{fila}'")


def processar_bilhete(ch, method, properties, body):
    data = json.loads(body)
    reserva_id = data.get("reserva_id")
    print(f"[MS RESERVA] Bilhete gerado para reserva {reserva_id}")
    atualizar_reserva_status(reserva_id, "bilhete_gerado")


def start_consuming():
    connection = pika.BlockingConnection(
        pika.ConnectionParameters(
            host=RABBITMQ_HOST,
            credentials=pika.PlainCredentials(RABBITMQ_USER, RABBITMQ_PASS),
        )
    )
    channel = connection.channel()

    # Declara as filas
    channel.queue_declare(queue="pagamento-aprovado")
    channel.queue_declare(queue="pagamento-recusado")
    channel.queue_declare(queue="bilhete-gerado")

    channel.basic_consume(
        queue="pagamento-aprovado",
        on_message_callback=processar_pagamento,
        auto_ack=True,
    )
    channel.basic_consume(
        queue="pagamento-recusado",
        on_message_callback=processar_pagamento,
        auto_ack=True,
    )
    channel.basic_consume(
        queue="bilhete-gerado", on_message_callback=processar_bilhete, auto_ack=True
    )

    print("[MS RESERVA] Aguardando mensagens de pagamento e bilhete...")
    channel.start_consuming()

if __name__ == "__main__":
    start_consuming()