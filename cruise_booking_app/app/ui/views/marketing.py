from flask import Blueprint, render_template, request, redirect, url_for
import threading
import pika
import json
from app.shared.config import RABBITMQ_HOST, RABBITMQ_USER, RABBITMQ_PASS

bp = Blueprint("marketing", __name__, url_prefix="/promocoes")

# Armazenamento temporário das promoções recebidas
mensagens_promocionais = []
destinos_escutando = set()


def callback_factory(destino):
    def processar(ch, method, properties, body):
        data = json.loads(body)
        mensagens_promocionais.append(data)
        print(f"[PROMOÇÃO {destino.upper()}] Recebida: {data.get('mensagem')}")
    return processar


def iniciar_listener_para(destino):
    if destino in destinos_escutando:
        return

    destinos_escutando.add(destino)
    fila = f"promocoes-destino_{destino.lower().replace(' ', '_')}"

    def listen():
        connection = pika.BlockingConnection(
            pika.ConnectionParameters(
                host=RABBITMQ_HOST,
                credentials=pika.PlainCredentials(RABBITMQ_USER, RABBITMQ_PASS)
            )
        )
        channel = connection.channel()
        channel.queue_declare(queue=fila)

        channel.basic_consume(
            queue=fila,
            on_message_callback=callback_factory(destino),
            auto_ack=True
        )

        print(f"[UI MARKETING] Escutando fila: {fila}")
        channel.start_consuming()

    t = threading.Thread(target=listen, daemon=True)
    t.start()


@bp.route("/", methods=["GET", "POST"])
def promocoes():
    if request.method == "POST":
        destino = request.form.get("destino")
        if destino:
            iniciar_listener_para(destino)

        return redirect(url_for("marketing.promocoes"))

    return render_template("promocoes.html", mensagens=mensagens_promocionais)
