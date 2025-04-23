import json
import logging
import uuid
from datetime import datetime
from pathlib import Path

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s",
    handlers=[logging.StreamHandler()],
)

RESERVAS_PATH = Path("app/ms_reserva/data/reservas.json")


def consultar_itinerarios(
    destino: str = "", data_embarque: str = "", porto_embarque: str = ""
):
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
            "datas_embarque": ["2025-07-10", "2025-08-10"],
        },
        {
            "id": "2",
            "navio": "Caribbean Sun",
            "porto_embarque": "Fortaleza",
            "porto_desembarque": "Fortaleza",
            "lugares_visitados": ["Barbados", "St. Lucia", "Bahamas"],
            "numero_noites": 10,
            "valor_por_pessoa": 4999.90,
            "datas_embarque": ["2025-09-10", "2025-10-10"],
        },
        {
            "id": "3",
            "navio": "Pacific Explorer",
            "porto_embarque": "Rio de Janeiro",
            "porto_desembarque": "Rio de Janeiro",
            "lugares_visitados": ["Salvador", "Recife", "Natal"],
            "numero_noites": 5,
            "valor_por_pessoa": 1999.90,
            "datas_embarque": ["2025-06-15", "2025-07-15"],
        },
        {
            "id": "4",
            "navio": "Mediterranean Breeze",
            "porto_embarque": "Barcelona",
            "porto_desembarque": "Barcelona",
            "lugares_visitados": ["Rome", "Athens", "Santorini"],
            "numero_noites": 12,
            "valor_por_pessoa": 5999.90,
            "datas_embarque": ["2025-05-20", "2025-06-20"],
        },
        {
            "id": "5",
            "navio": "Arctic Voyager",
            "porto_embarque": "Oslo",
            "porto_desembarque": "Oslo",
            "lugares_visitados": ["Bergen", "Tromsø", "Svalbard"],
            "numero_noites": 14,
            "valor_por_pessoa": 7999.90,
            "datas_embarque": ["2025-12-01", "2025-12-15"],
        },
        {
            "id": "6",
            "navio": "Asian Serenity",
            "porto_embarque": "Singapore",
            "porto_desembarque": "Singapore",
            "lugares_visitados": ["Bangkok", "Ho Chi Minh City", "Manila"],
            "numero_noites": 8,
            "valor_por_pessoa": 3999.90,
            "datas_embarque": ["2025-03-10", "2025-04-10"],
        },
        {
            "id": "7",
            "navio": "Southern Star",
            "porto_embarque": "Sydney",
            "porto_desembarque": "Sydney",
            "lugares_visitados": ["Melbourne", "Hobart", "Auckland"],
            "numero_noites": 9,
            "valor_por_pessoa": 4599.90,
            "datas_embarque": ["2025-11-05", "2025-12-05"],
        },
    ]

    # Se nenhum filtro for aplicado, retorna todos os itinerários
    if not destino and not data_embarque and not porto_embarque:
        return itinerarios

    return [
        itin
        for itin in itinerarios
        if destino.lower() in map(str.lower, itin["lugares_visitados"])
        and data_embarque in itin["datas_embarque"]
        and porto_embarque.lower() == itin["porto_embarque"].lower()
    ]


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
