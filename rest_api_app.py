from flask import Flask, request, jsonify
from flask_pymongo import PyMongo
from flask_cors import CORS

app = Flask(__name__)

CORS(app)
app.config["MONGO_URI"] = "mongodb://localhost:27017/crowdsourcing"  
mongo = PyMongo(app)
db = mongo.db

db['buson-306-01'].create_index("ssid", unique=True)

@app.route('/localizacao', methods=['POST']) 
def receber_localizacao():
    data = request.json
    print(f"Dados recebidos: {data}")  # Adicionando o log

    ssid = data.get("ssid")
    latitude = data.get("latitude")
    longitude = data.get("longitude")
    speed = data.get("speed")
    timestamp = data.get("timestamp")
    
    print(f"Tipo de ssid: {type(ssid)}")
    print(f"Tipo de latitude: {type(latitude)}")
    print(f"Tipo de longitude: {type(longitude)}")
    print(f"Tipo de speed: {type(speed)}")
    print(f"Tipo de timestamp: {type(timestamp)}")
    
    if not ssid or not isinstance(ssid, str):
        return jsonify({"erro": "SSID inválido"}), 400

    if not all([ssid, isinstance(latitude, (int, float)), isinstance(longitude, (int, float)), isinstance(speed, (int, float))]):
        return jsonify({"erro": "Todos os campos devem ser números e obrigatórios"}), 400

    try:
        # Agora, você vai atualizar a coleção 'buson-306-01'
        resultado = db['buson-306-01'].update_one(
            {"ssid": ssid},
            {"$set": {"latitude": latitude, 
                      "longitude": longitude, 
                      "speed": speed, 
                      "timestamp": timestamp}},
            upsert=True
        )
        mensagem = "Localização atualizada" if resultado.matched_count else "Nova localização inserida"
        return jsonify({"mensagem": mensagem}), 200
    except Exception as e:
        return jsonify({"erro": str(e)}), 500

@app.route('/localizacao/<ssid>', methods=['GET'])  # A rota também pode ser renomeada se necessário
def obter_localizacao_por_ssid(ssid):
    # Alterando a consulta para buscar na coleção 'buson-306-01'
    localizacao = db['buson-306-01'].find_one({"ssid": ssid}, {"_id": 0})
    if localizacao:
        return jsonify(localizacao), 200
    else:
        return jsonify({"erro": "SSID não encontrado"}), 404

if __name__ == '__main__':
    # Rodando o Flask para escutar em todas as interfaces de rede (0.0.0.0)
    host = '192.168.100.102'
    app.run(host=host, port=5000, debug=True)
