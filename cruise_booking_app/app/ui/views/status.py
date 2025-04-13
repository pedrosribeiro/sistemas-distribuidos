from flask import Blueprint, render_template
import json
from pathlib import Path

bp = Blueprint("status", __name__, url_prefix="/status")

RESERVAS_PATH = Path("app/ms_reserva/data/reservas.json")


@bp.route("/")
def listar_reservas():
    if RESERVAS_PATH.exists():
        with open(RESERVAS_PATH, "r", encoding="utf-8") as f:
            reservas = json.load(f)
    else:
        reservas = []

    return render_template("status.html", reservas=reservas)
