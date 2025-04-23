import json
import uuid
from datetime import datetime

from app.ms_reserva.publisher import publicar_reserva
from app.ms_reserva.service import consultar_itinerarios, criar_reserva
from flask import Blueprint, redirect, render_template, request, url_for

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


@bp.route(
    "/reservar/<itinerario_id>/<datas_embarque>/<valor_por_pessoa>",
    methods=["GET", "POST"],
)
def reservar(itinerario_id, datas_embarque, valor_por_pessoa):
    if request.method == "POST":
        cliente = request.form["cliente"]
        num_passageiros = int(request.form["num_passageiros"])
        num_cabines = int(request.form["num_cabines"])
        data_embarque = request.form["data_embarque"]
        valor_por_pessoa = float(request.form["valor_por_pessoa"])

        reserva = criar_reserva(
            itinerario_id,
            data_embarque,
            cliente,
            num_passageiros,
            valor_por_pessoa,
            num_cabines,
        )
        publicar_reserva(reserva)

        # Redireciona para página de confirmação, passando dados da reserva
        return render_template("confirmacao.html", reserva=reserva)

    # datas_embarque é uma string com datas separadas por vírgula
    datas_embarque = datas_embarque.split(",")

    return render_template(
        "reservar.html",
        itinerario_id=itinerario_id,
        datas_embarque=datas_embarque,
        valor_por_pessoa=valor_por_pessoa,
    )
