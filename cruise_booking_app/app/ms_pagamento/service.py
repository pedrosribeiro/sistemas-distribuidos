import json
import logging
import random

from app.ms_pagamento.publisher import publish_result
from app.shared.crypto_utils import load_private_key, sign_message

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s",
    handlers=[logging.StreamHandler()],
)

private_key = load_private_key("app/ms_pagamento/keys/private_key.pem")


def process_payment(reserva):
    aprovado = random.choice([True, True, True, False])

    resultado = {
        "reserva_id": reserva.get("reserva_id"),
        "valor": reserva.get("valor"),
        "status": "aprovado" if aprovado else "recusado",
    }

    # Serializa e assina
    msg_bytes = json.dumps(resultado).encode()
    assinatura = sign_message(msg_bytes, private_key)

    publish_result(resultado, assinatura, aprovado)
