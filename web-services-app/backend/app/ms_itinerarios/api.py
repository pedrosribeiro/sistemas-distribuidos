import json
import logging
from pathlib import Path

from flask import Flask, request, jsonify
from flask_cors import CORS

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s",
    handlers=[logging.StreamHandler()],
)

app = Flask(__name__)
CORS(app)

ITINERARIOS_PATH = Path("app/ms_itinerarios/itinerarios.json")

@app.route('/api/itinerarios', methods=['GET'])
def consultar_itinerarios():
    """Consultar itinerários disponíveis"""
    try:
        destino = request.args.get('destino', '')
        data_embarque = request.args.get('data_embarque', '')
        porto_embarque = request.args.get('porto_embarque', '')
        
        # Carregar itinerários do arquivo JSON
        if not ITINERARIOS_PATH.exists():
            return jsonify([])
        
        with open(ITINERARIOS_PATH, "r", encoding="utf-8") as f:
            itinerarios = json.load(f)
        
        # Filtrar itinerários com base nos parâmetros
        itinerarios_filtrados = []
        for itinerario in itinerarios:
            # Filtrar por destino (se especificado)
            if destino and destino.lower() not in ' '.join(itinerario.get('lugares_visitados', [])).lower():
                continue
            
            # Filtrar por porto de embarque (se especificado)
            if porto_embarque and porto_embarque.lower() not in itinerario.get('porto_embarque', '').lower():
                continue
            
            # Filtrar por data de embarque (se especificada)
            if data_embarque and data_embarque not in itinerario.get('datas_embarque', []):
                continue
            
            itinerarios_filtrados.append(itinerario)
        
        return jsonify(itinerarios_filtrados)
        
    except Exception as e:
        return jsonify({"erro": "Erro interno do servidor"}), 500

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5002, debug=True)
