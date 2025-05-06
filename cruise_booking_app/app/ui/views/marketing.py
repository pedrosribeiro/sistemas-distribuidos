import json
import logging
import threading
import uuid

import pika
from app.shared.config import RABBITMQ_HOST, RABBITMQ_PASS, RABBITMQ_USER
from flask import Blueprint, redirect, render_template, request, session, url_for

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s",
    handlers=[logging.StreamHandler()],
)

bp = Blueprint("marketing", __name__, url_prefix="/promocoes")


def get_session_id():
    if "session_id" not in session:
        session["session_id"] = str(uuid.uuid4())
    return session["session_id"]


# Armazenamento por sessão (em memória, para simulação)
session_listeners = {}
session_messages = {}


def callback_factory(destino, session_id):
    def processar(ch, method, properties, body):
        data = json.loads(body)
        if session_id not in session_messages:
            session_messages[session_id] = []
        if data not in session_messages[session_id]:
            session_messages[session_id].append(data)
        logging.info(
            f"[PROMOÇÃO {destino.upper()}][{session_id}] Recebida: {data.get('mensagem')}"
        )

    return processar


def iniciar_listener_para(destino):
    session_id = get_session_id()
    if session_id not in session_listeners:
        session_listeners[session_id] = set()
    if destino in session_listeners[session_id]:
        return

    session_listeners[session_id].add(destino)
    
    fila = f"promocoes-destino_{destino.lower().replace(' ', '_')}_{session_id}"

    def listen():
        connection = pika.BlockingConnection(
            pika.ConnectionParameters(
                host=RABBITMQ_HOST,
                credentials=pika.PlainCredentials(RABBITMQ_USER, RABBITMQ_PASS),
            )
        )
        channel = connection.channel()

        channel.exchange_declare(exchange="promocoes_exchange", exchange_type="direct")
        
        result = channel.queue_declare(queue=fila, exclusive=True)
        channel.queue_bind(
            exchange="promocoes_exchange", queue=fila, routing_key=destino
        )

        channel.basic_consume(
            queue=fila,
            on_message_callback=callback_factory(destino, session_id),
            auto_ack=True,
        )

        logging.info(f"[UI MARKETING][{session_id}] Escutando fila: {fila}")
        channel.start_consuming()

    t = threading.Thread(target=listen, daemon=True)
    t.start()


@bp.route("/", methods=["GET", "POST"])
def promocoes():
    session_id = get_session_id()
    if request.method == "POST":
        destino = request.form.get("destino")
        if destino:
            iniciar_listener_para(destino)
        return redirect(url_for("marketing.promocoes"))

    mensagens = session_messages.get(session_id, [])
    return render_template("promocoes.html", mensagens=mensagens)
