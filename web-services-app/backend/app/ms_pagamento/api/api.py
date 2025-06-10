import json
import logging
import uuid
import requests
from datetime import datetime

from app.ms_pagamento.rabbitmq import publicar_pagamento_aprovado, publicar_pagamento_recusado
from flask import Flask, request, jsonify
from flask_cors import CORS

app = Flask(__name__)
CORS(app)

EXTERNAL_PAYMENT_SERVICE="http://external_payment_service:5050/api/external/pay"

@app.route('/api/pagamento/link', methods=['POST'])
def gerar_link_pagamento():
    """Gerar link de pagamento para uma reserva"""
    dados = request.get_json()
    
    # Validar dados obrigatórios
    campos_obrigatorios = ['reserva_id', 'valor', 'cliente_id']
    for campo in campos_obrigatorios:
        if campo not in dados:
            return jsonify({"erro": f"Campo obrigatório ausente: {campo}"}), 400
    
    response = requests.post(
        EXTERNAL_PAYMENT_SERVICE,
        json={
            'valor': dados['valor'],
            'moeda': "real",
            'reserva_id': dados['reserva_id'],
            'cliente_id': dados['cliente_id']
        },
        timeout=10
    )
    
    if response.status_code == 200:
        return jsonify(response.json()), 200
    else:
        return jsonify({"erro": "Erro ao gerar link de pagamento"}), 500
    
@app.route('/api/pagamento/webhook', methods=['POST'])
def atualizar_status_pagamento():
    """Consultar status de pagamento de uma reserva"""
    data = request.get_json()
    status = data.get("status")
    reserva_id = data.get("reserva_id")

    if (status == "aprovado"):
        publicar_pagamento_aprovado(reserva_id)
    else:
        publicar_pagamento_recusado(reserva_id)

    return jsonify({})

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5003, debug=True)