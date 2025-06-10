import json
import logging
import uuid
from datetime import datetime
from pathlib import Path

from flask import Flask, request, jsonify, Response
from flask_cors import CORS
import requests
import threading
import time
import json
import uuid

from datetime import datetime
from pathlib import Path
from app.ms_reserva.rabbitmq import publicar_reserva

RESERVAS_PATH = Path("app/ms_reserva/data/reservas.json")

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s",
    handlers=[logging.StreamHandler()],
)

app = Flask(__name__)
CORS(app)

# Armazenamento em memória para conexões SSE
sse_connections = {}
promocoes_connections = {}

ITINERARIOS_SERVICE_URL = "http://ms_itinerarios_api:5002"
PAGAMENTO_SERVICE_URL = "http://ms_pagamento_api:5003"

@app.route('/api/itinerarios', methods=['GET'])
def consultar_itinerarios():
    """Consultar itinerários disponíveis"""
    destino = request.args.get('destino', '')
    data_embarque = request.args.get('data_embarque', '')
    porto_embarque = request.args.get('porto_embarque', '')

    # Fazer requisição REST para o MS Itinerários
    response = requests.get(
        f"{ITINERARIOS_SERVICE_URL}/api/itinerarios",
        params={
            'destino': destino,
            'data_embarque': data_embarque,
            'porto_embarque': porto_embarque
        },
        timeout=10
    )

    response.raise_for_status()
    itinerarios = response.json()
    if not itinerarios:
        return jsonify([]), 501
    
    return jsonify(itinerarios), 200

@app.route('/api/itinerarios/<int:itinerarioId>', methods=['GET'])
def get_itinerario(itinerarioId):
    # Fazer requisição REST para o MS Itinerários
    response = requests.get(
        f"{ITINERARIOS_SERVICE_URL}/api/itinerarios/{itinerarioId}",
        timeout=10
    )

    response.raise_for_status()
    itinerario = response.json()
    if not itinerario:
        return jsonify([]), 501
    
    return jsonify(itinerario), 200

@app.route('/api/reservas', methods=['POST'])
def efetuar_reserva():
    """Efetuar uma reserva"""
    try:
        dados = request.get_json()
        
        # Validar dados obrigatórios
        campos_obrigatorios = ['itinerario_id', 'data_embarque', 'numero_passageiros', 'numero_cabines', 'cliente_id', 'valor_por_pessoa']
        for campo in campos_obrigatorios:
            if campo not in dados:
                return jsonify({"erro": f"Campo obrigatório ausente: {campo}"}), 400
        
        # Criar a reserva
        reserva = criar_reserva(
            itinerario_id=dados['itinerario_id'],
            data_embarque=dados['data_embarque'],
            numero_passageiros=dados['numero_passageiros'],
            numero_cabines=dados['numero_cabines'],
            cliente_id=dados['cliente_id'],
            valor_por_pessoa=dados['valor_por_pessoa'],
        )
        
        if not reserva:
            return jsonify({"erro": "Erro ao criar reserva"}), 500
        
        # Publicar evento de reserva criada
        publicar_reserva(reserva)
        
        # Solicitar link de pagamento ao MS Pagamento
        try:
            response = requests.post(
                f"{PAGAMENTO_SERVICE_URL}/api/pagamento/link",
                json={
                    'reserva_id': reserva['reserva_id'],
                    'valor': reserva['valor'],
                    'cliente_id': reserva['cliente_id']
                },
                timeout=10
            )
            if response.status_code == 200:
                try:
                    pagamento_data = response.json()
                    reserva['link_pagamento'] = pagamento_data.get('link_pagamento')
                except Exception as e:
                    reserva['link_pagamento'] = 'PRIMEIRA'
                    logging.error(f"Erro ao decodificar JSON do pagamento: {e}")
            else:
                reserva['link_pagamento'] = 'SEGUNDOI'
                logging.error(f"Erro ao solicitar link de pagamento: {response.status_code} {response.text}")
        except Exception as e:
            reserva['link_pagamento'] = 'TECERIRO'
            logging.error(f"Erro na requisição ao MS Pagamento: {e}")
        
        return jsonify(reserva), 201

    except Exception as e:
        return jsonify({"erro": f"{e}"}), 500


@app.route('/api/reservas/<reserva_id>/cancelar', methods=['DELETE'])
def cancelar_reserva_endpoint(reserva_id):
    """Cancelar uma reserva"""
    try:
        # Carregar reservas
        if not RESERVAS_PATH.exists():
            return jsonify({"erro": "Reserva não encontrada"}), 404
        with open(RESERVAS_PATH, "r", encoding="utf-8") as f:
            reservas = json.load(f)
        reserva_cancelada = None
        for reserva in reservas:
            if reserva["reserva_id"] == reserva_id:
                reserva_cancelada = reserva
                reservas.remove(reserva)
                break
        if not reserva_cancelada:
            return jsonify({"erro": "Reserva não encontrada"}), 404
        # Salvar reservas atualizadas
        with open(RESERVAS_PATH, "w", encoding="utf-8") as f:
            json.dump(reservas, f, indent=2)
        # Publicar evento na fila 'reserva-cancelada'
        from app.ms_reserva.rabbitmq import publicar_reserva_cancelada
        publicar_reserva_cancelada(reserva_cancelada)
        return jsonify({"mensagem": "Reserva cancelada com sucesso"}), 200
    except Exception as e:
        return jsonify({"erro": f"Erro interno do servidor: {str(e)}"}), 500

# @app.route('/api/promocoes/interesse', methods=['POST'])
# def registrar_interesse():
#     """Registrar interesse em receber notificações de promoções"""
#     try:
#         dados = request.get_json()
        
#         if 'cliente_id' not in dados:
#             return jsonify({"erro": "Campo obrigatório ausente: cliente_id"}), 400
        
#         cliente_id = dados['cliente_id']
#         resultado = registrar_interesse_promocoes(cliente_id)
        
#         if resultado:
#             logging.info(f"[MS RESERVA] Interesse em promoções registrado: {cliente_id}")
#             return jsonify({"mensagem": "Interesse registrado com sucesso"}), 201
#         else:
#             return jsonify({"erro": "Erro ao registrar interesse"}), 500
            
#     except Exception as e:
#         logging.error(f"[MS RESERVA] Erro ao registrar interesse: {str(e)}")
#         return jsonify({"erro": "Erro interno do servidor"}), 500

# @app.route('/api/promocoes/interesse/<cliente_id>', methods=['DELETE'])
# def cancelar_interesse(cliente_id):
#     """Cancelar interesse em receber notificações de promoções"""
#     try:
#         resultado = cancelar_interesse_promocoes(cliente_id)
        
#         if resultado:
#             logging.info(f"[MS RESERVA] Interesse em promoções cancelado: {cliente_id}")
#             return jsonify({"mensagem": "Interesse cancelado com sucesso"}), 200
#         else:
#             return jsonify({"erro": "Cliente não encontrado"}), 404
            
#     except Exception as e:
#         logging.error(f"[MS RESERVA] Erro ao cancelar interesse: {str(e)}")
#         return jsonify({"erro": "Erro interno do servidor"}), 500

# @app.route('/api/sse/reserva/<cliente_id>')
# def sse_reserva(cliente_id):
#     """Endpoint SSE para notificações de reserva"""
#     def event_stream():
#         # Registrar conexão
#         sse_connections[cliente_id] = True
#         logging.info(f"[MS RESERVA] Cliente conectado ao SSE de reserva: {cliente_id}")
        
#         try:
#             while sse_connections.get(cliente_id, False):
#                 # Manter conexão viva
#                 yield f"data: {json.dumps({'tipo': 'heartbeat', 'timestamp': datetime.now().isoformat()})}\n\n"
#                 time.sleep(30)
#         except GeneratorExit:
#             logging.info(f"[MS RESERVA] Cliente desconectado do SSE de reserva: {cliente_id}")
#             sse_connections.pop(cliente_id, None)
    
#     return Response(event_stream(), mimetype='text/event-stream')

# @app.route('/api/sse/promocoes/<cliente_id>')
# def sse_promocoes(cliente_id):
#     """Endpoint SSE para notificações de promoções"""
#     def event_stream():
#         # Registrar conexão
#         promocoes_connections[cliente_id] = True
#         logging.info(f"[MS RESERVA] Cliente conectado ao SSE de promoções: {cliente_id}")
        
#         try:
#             while promocoes_connections.get(cliente_id, False):
#                 # Manter conexão viva
#                 yield f"data: {json.dumps({'tipo': 'heartbeat', 'timestamp': datetime.now().isoformat()})}\n\n"
#                 time.sleep(30)
#         except GeneratorExit:
#             logging.info(f"[MS RESERVA] Cliente desconectado do SSE de promoções: {cliente_id}")
#             promocoes_connections.pop(cliente_id, None)
    
#     return Response(event_stream(), mimetype='text/event-stream')

@app.route('/api/reservas', methods=['GET'])
def obter_reservas():
    """Obter detalhes de uma reserva"""
    try:
        reserva = obter_todas_reservas()
        
        if reserva:
            return jsonify(reserva)
        else:
            return jsonify([]), 404
            
    except Exception as e:
        logging.error(f"[MS RESERVA] Erro ao obter reserva: {str(e)}")
        return jsonify({"erro": "Erro interno do servidor"}), 500

def enviar_notificacao_sse(cliente_id, dados, tipo_conexao='reserva'):
    """Enviar notificação via SSE para um cliente específico"""
    connections = sse_connections if tipo_conexao == 'reserva' else promocoes_connections
    
    if cliente_id in connections:
        try:
            # Em uma implementação real, você precisaria de um mecanismo mais sofisticado
            # para enviar dados através das conexões SSE ativas
            logging.info(f"[MS RESERVA] Notificação SSE enviada para {cliente_id}: {dados}")
        except Exception as e:
            logging.error(f"[MS RESERVA] Erro ao enviar notificação SSE: {str(e)}")
            connections.pop(cliente_id, None)

def criar_reserva(
    itinerario_id,
    data_embarque,
    cliente_id,
    numero_passageiros,
    valor_por_pessoa,
    numero_cabines,
):
    reserva = {
        "reserva_id": str(uuid.uuid4()),
        "itinerario_id": itinerario_id,
        "data_embarque": data_embarque,
        "cliente_id": cliente_id,
        "numero_passageiros": numero_passageiros,
        "numero_cabines": numero_cabines,
        "valor": valor_por_pessoa * numero_passageiros,
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

def obter_todas_reservas():
    if not RESERVAS_PATH.exists():
        return False
    
    with open(RESERVAS_PATH, "r", encoding="utf-8") as f:
        reservas = json.load(f)

    if not reservas:
        return []
        
    return reservas
            
        
if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5001, debug=True)
