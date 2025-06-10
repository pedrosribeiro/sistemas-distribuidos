import json
import logging
from pathlib import Path

import pika
from app.shared.config import RABBITMQ_HOST, RABBITMQ_PASS, RABBITMQ_USER

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s",
    handlers=[logging.StreamHandler()],
)

RESERVAS_PATH = Path("app/ms_reserva/data/reservas.json")

def atualizar_reserva_status_pagamento(reserva_id, novo_status):
    if not RESERVAS_PATH.exists():
        logging.info(f"[MS RESERVA] Arquivo de reservas não encontrado.")
        return

    with open(RESERVAS_PATH, "r", encoding="utf-8") as f:
        reservas = json.load(f)

    for r in reservas:
        if r["reserva_id"] == reserva_id:
            r["status_pagamento"] = novo_status
            break

    with open(RESERVAS_PATH, "w", encoding="utf-8") as f:
        json.dump(reservas, f, indent=2)

    logging.info(
        f"[MS RESERVA] Status pagamento atualizado para '{novo_status}' (reserva_id: {reserva_id})"
    )


def atualizar_reserva_status_bilhete(reserva_id, novo_status):
    if not RESERVAS_PATH.exists():
        logging.info(f"[MS RESERVA] Arquivo de reservas não encontrado.")
        return

    with open(RESERVAS_PATH, "r", encoding="utf-8") as f:
        reservas = json.load(f)

    for r in reservas:
        if r["reserva_id"] == reserva_id:
            r["status_bilhete"] = novo_status
            break

    with open(RESERVAS_PATH, "w", encoding="utf-8") as f:
        json.dump(reservas, f, indent=2)

    logging.info(
        f"[MS RESERVA] Status bilhete atualizado para '{novo_status}' (reserva_id: {reserva_id})"
    )


def processar_pagamento(ch, method, properties, body):
    data = json.loads(body)

    resultado = data.get("resultado")  # aprovado ou recusado
    reserva_id = data.get("reserva_id")

    atualizar_reserva_status_pagamento(reserva_id, resultado)


def processar_bilhete(ch, method, properties, body):
    data = json.loads(body)
    reserva_id = data.get("reserva_id")
    logging.info(f"[MS RESERVA] Bilhete gerado para reserva {reserva_id}")
    atualizar_reserva_status_bilhete(reserva_id, "bilhete_gerado")


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
    pagamento_aprovado_queue = result.method.queue
    channel.queue_bind(
        exchange="pagamento-aprovado-exchange", queue=pagamento_aprovado_queue
    )

    # Continua declarando as outras filas normalmente
    channel.queue_declare(queue="pagamento-recusado")
    channel.queue_declare(queue="bilhete-gerado")

    channel.basic_consume(
        queue=pagamento_aprovado_queue,
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

    logging.info(
        "[MS RESERVA] Aguardando mensagens de pagamento e bilhete (pagamento-aprovado via exchange fanout)..."
    )
    channel.start_consuming()
