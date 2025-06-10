from flask import Flask, request, jsonify
import uuid
from datetime import datetime
import time
import random

import requests

app = Flask(__name__)

@app.route('/api/external/pay', methods=['POST'])
def external_pay():
    data = request.get_json()

    valor = data.get("valor")
    moeda = data.get("moeda")
    cliente_id = data.get("cliente_id")
    reserva_id = data.get("reserva_id")

    # Simula processamento do pagamento
    link_pagamento = f"http://localhost:5050/api/external/pay/link/{reserva_id}"
    response = {
        "link_pagamento": link_pagamento,
        "status": "pagamento_pendente",
        "valor": valor,
        "cliente_id": cliente_id,
        "reserva_id": reserva_id,
        "data_criacao": datetime.now().isoformat()
    }

    return jsonify(response), 200

@app.route('/api/external/pay/link/<string:reserva_id>', methods=['GET'])
def simulate_payment(reserva_id):
    status = random.choice(["aprovado", "recusado"])

    # Aguarda alguns segundos para simular o pagamento
    time.sleep(2)

    # Envia notificação para o ms_pagamento
    payload = {
        "status": status,
        "reserva_id": reserva_id
    }

    requests.post("http://ms_pagamento_api:5003/api/pagamento/webhook", json=payload, timeout=2)

    return f"Pagamento {status}! Notificação enviada.", 200

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5050)
