import json
import uuid
from datetime import datetime
from pathlib import Path

RESERVAS_PATH = Path("app/ms_reserva/data/reservas.json")

def criar_reserva(
    itinerario_id,
    data_embarque,
    cliente,
    num_passageiros,
    valor_por_pessoa,
    num_cabines,
):
    reserva = {
        "reserva_id": str(uuid.uuid4()),
        "itinerario_id": itinerario_id,
        "data_embarque": data_embarque,
        "cliente": cliente,
        "num_passageiros": num_passageiros,
        "num_cabines": num_cabines,
        "valor": valor_por_pessoa * num_passageiros,
        "status_pagamento": "pagamento_pendente",
        "status_bilhete": "nao_gerado",
        "data_criacao": datetime.now().isoformat(),
    }

    salvar_reserva(reserva)
    return reserva


def salvar_reserva(reserva):
    RESERVAS_PATH.parent.mkdir(parents=True, exist_ok=True)
    if RESERVAS_PATH.exists():
        with open(RESERVAS_PATH, "r", encoding="utf-8") as f:
            reservas = json.load(f)
    else:
        reservas = []

    reservas.append(reserva)

    with open(RESERVAS_PATH, "w", encoding="utf-8") as f:
        json.dump(reservas, f, indent=2)


def cancelar_reserva(reserva_id):
    if not RESERVAS_PATH.exists():
        return False
    
    with open(RESERVAS_PATH, "r", encoding="utf-8") as f:
        reservas = json.load(f)
    
    for reserva in reservas:
        if reserva["reserva_id"] == reserva_id:
            reservas.remove(reserva)
            return True
    return False