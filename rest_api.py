from flask import Flask, request, jsonify
from flask_pymongo import PyMongo

app = Flask(__name__)

# Alterando o banco de dados para 'crowdsourcing'
app.config["MONGO_URI"] = "mongodb://localhost:27017/crowdsourcing"  
mongo = PyMongo(app)
db = mongo.db

# Agora, vamos trabalhar com a coleção 'buson-306-01'
db['buson-306-01'].create_index("ssid", unique=True)

@app.route('/localizacao', methods=['POST'])  # A rota não precisa mudar, mas pode ser renomeada se necessário
def receber_localizacao():
    data = request.json
    ssid = data.get("ssid")
    latitude = data.get("latitude")
    longitude = data.get("longitude")
    velocidade = data.get("velocidade")
    timestamp = data.get("timestamp")

    if not all([ssid, latitude, longitude, velocidade]):
        return jsonify({"erro": "Todos os campos são obrigatórios"}), 400

    try:
        # Agora, você vai atualizar a coleção 'buson-306-01'
        resultado = db['buson-306-01'].update_one(
            {"ssid": ssid},
            {"$set": {"latitude": latitude, 
                      "longitude": longitude, 
                      "velocidade": velocidade, 
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
    app.run(debug=True)
