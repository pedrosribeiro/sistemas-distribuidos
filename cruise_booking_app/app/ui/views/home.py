import json
import uuid
from datetime import datetime

from flask import Blueprint, redirect, render_template, request, url_for

from app.ms_reserva.publisher import publicar_reserva
from app.ms_reserva.service import consultar_itinerarios, criar_reserva

bp = Blueprint("home", __name__)


@bp.route("/")
def index():
    itinerarios = consultar_itinerarios()
    return render_template("home.html", itinerarios=itinerarios)


@bp.route("/itinerarios", methods=["POST"])
def mostrar_itinerarios():
    destino = request.form["destino"]
    data = request.form["data_embarque"]
    porto = request.form["porto_embarque"]

    lista = consultar_itinerarios(destino, data, porto)
    return render_template(
        "home.html", itinerarios=lista, destino=destino, data=data, porto=porto
    )


@bp.route("/reservar/<itinerario_id>", methods=["GET", "POST"])
def reservar(itinerario_id):
    if request.method == "POST":
        cliente = request.form["cliente"]
        num_passageiros = int(request.form["num_passageiros"])
        num_cabines = int(request.form["num_cabines"])
        valor = float(request.form["valor"])
        data_embarque = request.form["data_embarque"]

        reserva = criar_reserva(
            itinerario_id, data_embarque, cliente, num_passageiros, num_cabines, valor
        )
        publicar_reserva(reserva)

        # Redireciona para página de confirmação, passando dados da reserva
        return render_template("confirmacao.html", reserva=reserva)

    return render_template("reservar.html", itinerario_id=itinerario_id)
