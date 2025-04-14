import json
import uuid
from datetime import datetime
from pathlib import Path

RESERVAS_PATH = Path("app/ms_reserva/data/reservas.json")


def consultar_itinerarios(destino: str = "", data_embarque: str = "", porto_embarque: str = ""):
    # Simulação de base de dados de itinerários
    itinerarios = [
        {
            "id": "1",
            "navio": "Oceanic Dream",
            "porto_embarque": "Santos",
            "porto_desembarque": "Santos",
            "lugares_visitados": ["Ilhabela", "Rio de Janeiro", "Búzios"],
            "numero_noites": 7,
            "valor_por_pessoa": 2999.90,
            "datas_disponiveis": ["2025-07-10", "2025-08-15"],
        },
        {
            "id": "2",
            "navio": "Caribbean Sun",
            "porto_embarque": "Fortaleza",
            "porto_desembarque": "Fortaleza",
            "lugares_visitados": ["Barbados", "St. Lucia", "Bahamas"],
            "numero_noites": 10,
            "valor_por_pessoa": 4999.90,
            "datas_disponiveis": ["2025-07-15", "2025-09-01"],
        },
    ]

    # Se nenhum filtro for aplicado, retorna todos os itinerários
    if not destino and not data_embarque and not porto_embarque:
        return itinerarios

    return [
        itin
        for itin in itinerarios
        if destino.lower() in map(str.lower, itin["lugares_visitados"])
        and data_embarque in itin["datas_disponiveis"]
        and porto_embarque.lower() == itin["porto_embarque"].lower()
    ]


def criar_reserva(
    itinerario_id, data_embarque, cliente, num_passageiros, num_cabines, valor
):
    reserva = {
        "reserva_id": str(uuid.uuid4()),
        "itinerario_id": itinerario_id,
        "data_embarque": data_embarque,
        "cliente": cliente,
        "num_passageiros": num_passageiros,
        "num_cabines": num_cabines,
        "valor": valor,
        "status": "pagamento_pendente",
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
