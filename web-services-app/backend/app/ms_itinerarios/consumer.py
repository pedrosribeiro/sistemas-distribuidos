import json
import logging
import pika
from pathlib import Path
from app.shared.config import RABBITMQ_HOST, RABBITMQ_USER, RABBITMQ_PASS

ITINERARIOS_PATH = Path("app/ms_itinerarios/itinerarios.json")

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s",
    handlers=[logging.StreamHandler()],
)

def atualizar_cabines(itinerario_id, data_embarque, numero_cabines, operacao):

    if not ITINERARIOS_PATH.exists():
        return
    with open(ITINERARIOS_PATH, "r", encoding="utf-8") as f:
        itinerarios = json.load(f)
    for itinerario in itinerarios:
        if str(itinerario["id"]) == str(itinerario_id):
            for data in itinerario.get("datas_embarque", []):
                if data == data_embarque:
                    if operacao == "reserva-criada":
                        itinerario["cabines_disponiveis"] = max(0, itinerario.get("cabines_disponiveis", 0) - numero_cabines)
                    elif operacao == "reserva-cancelada":
                        itinerario["cabines_disponiveis"] = itinerario.get("cabines_disponiveis", 0) + numero_cabines
    with open(ITINERARIOS_PATH, "w", encoding="utf-8") as f:
        json.dump(itinerarios, f, ensure_ascii=False, indent=2)


def callback_reserva_criada(ch, method, properties, body):
    data = json.loads(body)
    itinerario_id = data.get("itinerario_id")
    data_embarque = data.get("data_embarque")
    numero_cabines = data.get("numero_cabines", 1)
    atualizar_cabines(itinerario_id, data_embarque, numero_cabines, "reserva-criada")
    logging.info(f"Reserva criada processada para itinerario {itinerario_id}")


def callback_reserva_cancelada(ch, method, properties, body):
    data = json.loads(body)
    itinerario_id = data.get("itinerario_id")
    data_embarque = data.get("data_embarque")
    numero_cabines = data.get("numero_cabines", 1)
    atualizar_cabines(itinerario_id, data_embarque, numero_cabines, "reserva-cancelada")
    logging.info(f"Reserva cancelada processada para itinerario {itinerario_id}")


def start_consuming():
    connection = pika.BlockingConnection(
        pika.ConnectionParameters(
            host=RABBITMQ_HOST,
            credentials=pika.PlainCredentials(RABBITMQ_USER, RABBITMQ_PASS),
        )
    )
    channel = connection.channel()
    channel.queue_declare(queue="reserva-criada")
    channel.queue_declare(queue="reserva-cancelada")
    channel.basic_consume(queue="reserva-criada", on_message_callback=callback_reserva_criada, auto_ack=True)
    channel.basic_consume(queue="reserva-cancelada", on_message_callback=callback_reserva_cancelada, auto_ack=True)
    logging.info("[MS ITINERARIOS] Aguardando eventos de reserva-criada e reserva-cancelada...")
    channel.start_consuming()


if __name__ == "__main__":
    start_consuming()
