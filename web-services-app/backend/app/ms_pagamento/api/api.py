import json
import logging
import uuid
from datetime import datetime

from app.ms_pagamento.rabbitmq import publicar_pagamento_aprovado, publicar_pagamento_rejeitado
from flask import Flask, request, jsonify
from flask_cors import CORS

app = Flask(__name__)
CORS(app)

@app.route('/api/pagamento/link', methods=['POST'])
def gerar_link_pagamento():
    """Gerar link de pagamento para uma reserva"""
    try:
        dados = request.get_json()
        
        # Validar dados obrigatórios
        campos_obrigatorios = ['reserva_id', 'valor', 'cliente_id']
        for campo in campos_obrigatorios:
            if campo not in dados:
                return jsonify({"erro": f"Campo obrigatório ausente: {campo}"}), 400
        
        # Simular geração de link de pagamento
        transacao_id = str(uuid.uuid4())
        link_pagamento = f"https://pagamento-externo.com/pay/{transacao_id}"
        
        response_data = {
            "transacao_id": transacao_id,
            "link_pagamento": link_pagamento,
            "reserva_id": dados['reserva_id'],
            "valor": dados['valor'],
            "status": "pendente",
            "data_criacao": datetime.now().isoformat()
        }
        
        return jsonify(response_data), 200
        
    except Exception as e:
        return jsonify({"erro": "Erro interno do servidor"}), 500
    
@app.route('/api/pagamento/status', methods=['GET'])
def atualizar_status_pagamento():
    """Consultar status de pagamento de uma reserva"""
    status = request.get_json()

    if(status == "pago"):
        publicar_pagamento_aprovado(status, "assinatura")
    else:
        publicar_pagamento_rejeitado(status, "assinatura")

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5003, debug=True)