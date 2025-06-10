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
from app.ms_reserva.rabbitmq import publicar_reserva_cancelada

from queue import Queue


RESERVAS_PATH = Path("app/ms_reserva/data/reservas.json")
INTERESSES_PATH = Path("app/ms_reserva/data/interesses_promocoes.json")

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
                reserva["status_pagamento"] = "reserva_cancelada"
                reserva["status_bilhete"] = "reserva_cancelada"
                reserva_cancelada = reserva
                break

        if not reserva_cancelada:
            return jsonify({"erro": "Reserva não encontrada"}), 404
   
        with open(RESERVAS_PATH, "w", encoding="utf-8") as f:
            json.dump(reservas, f, indent=2)
     
        publicar_reserva_cancelada(reserva_cancelada)

        return jsonify({"mensagem": "Reserva cancelada com sucesso"}), 200
    except Exception as e:
        return jsonify({"erro": f"Erro interno do servidor: {str(e)}"}), 500

def registrar_interesse_promocoes(cliente_id):
    INTERESSES_PATH.parent.mkdir(parents=True, exist_ok=True)
    if INTERESSES_PATH.exists():
        with open(INTERESSES_PATH, "r", encoding="utf-8") as f:
            interesses = json.load(f)
    else:
        interesses = []
    if cliente_id not in interesses:
        interesses.append(cliente_id)
        with open(INTERESSES_PATH, "w", encoding="utf-8") as f:
            json.dump(interesses, f, indent=2)
        return True
    return False

def cancelar_interesse_promocoes(cliente_id):
    if not INTERESSES_PATH.exists():
        return False
    with open(INTERESSES_PATH, "r", encoding="utf-8") as f:
        interesses = json.load(f)
    if cliente_id in interesses:
        interesses.remove(cliente_id)
        with open(INTERESSES_PATH, "w", encoding="utf-8") as f:
            json.dump(interesses, f, indent=2)
        return True
    return False


def event_stream(cliente_id, connections):
    q = Queue()
    connections[cliente_id] = q
    logging.info(f"[MS RESERVA] Cliente conectado ao SSE: {cliente_id}")
    try:
        while True:
            try:
                # Espera uma mensagem por até 30 segundos
                mensagem = q.get(timeout=30)
            except:
                # Envia heartbeat se não houver mensagem
                mensagem = {"tipo": "heartbeat", "timestamp": datetime.now().isoformat()}
            yield f"data: {json.dumps(mensagem)}\n\n"
    except GeneratorExit:
        logging.info(f"[MS RESERVA] Cliente desconectado do SSE: {cliente_id}")
        connections.pop(cliente_id, None)


@app.route('/api/sse/<tipo>/<cliente_id>', methods=['GET'])
def sse_notificacoes(tipo, cliente_id):
    connections = sse_connections if tipo == 'reserva' else promocoes_connections
    return Response(event_stream(cliente_id, connections), mimetype='text/event-stream')


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

@app.route('/api/enviar_notificacao_sse', methods=['POST'])
def enviar_notificacao_sse():
    """Enviar notificação via SSE para um cliente específico"""
    dados_requisicao = request.get_json()
    cliente_id = dados_requisicao.get('cliente_id')
    mensagem = dados_requisicao.get('mensagem')
    tipo_conexao = dados_requisicao.get('tipo_conexao', 'reserva')

    connections = sse_connections if tipo_conexao == 'reserva' else promocoes_connections
    conn = connections.get(cliente_id)

    if conn:
        try:
            payload = {"tipo": "notificacao", "mensagem": mensagem}
            conn.put(payload)  # insere na fila
            logging.info(f"[MS RESERVA] Notificação SSE enviada para {cliente_id}: {payload}")
            return jsonify({"mensagem": "Notificação enviada"}), 200
        except Exception as e:
            logging.error(f"[MS RESERVA] Erro ao enviar notificação SSE: {str(e)}")
            connections.pop(cliente_id, None)
            return jsonify({"erro": "Erro ao enviar notificação"}), 500
    else:
        logging.warning(f"[MS RESERVA] Nenhuma conexão SSE ativa para {cliente_id}")
        return jsonify({"erro": "Nenhuma conexão SSE ativa para o cliente"}), 404

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
