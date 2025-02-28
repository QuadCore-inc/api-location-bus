from flask import Flask, request, jsonify
from flask_pymongo import PyMongo
import time

app = Flask(__name__)
# Conexão com o MongoDB (banco 'crowdsourcing')
app.config["MONGO_URI"] = "mongodb://localhost:27017/crowdsourcing"
mongo = PyMongo(app)
db = mongo.db

# Dicionário global para armazenar a última atualização de cada passageiro por ônibus
latest_updates = {}

@app.route('/update', methods=['POST'])
def update_location():
    data = request.get_json()

    # Validação dos campos obrigatórios
    required_fields = ["ssid", "passenger_id", "latitude", "longitude", "velocidade", "timestamp"]
    for field in required_fields:
        if field not in data:
            return jsonify({"error": f"O campo {field} é obrigatório"}), 400

    ssid = data["ssid"]
    passenger_id = data["passenger_id"]

    # Atualiza (ou cria) a entrada para o ônibus e o passageiro
    if ssid not in latest_updates:
        latest_updates[ssid] = {}
    latest_updates[ssid][passenger_id] = data

    # Cálculo da média dos valores a partir da última atualização de cada passageiro
    passenger_data = list(latest_updates[ssid].values())
    total = len(passenger_data)
    if total > 0:
        avg_lat = sum([d["latitude"] for d in passenger_data]) / total
        avg_lon = sum([d["longitude"] for d in passenger_data]) / total
        avg_speed = sum([d["velocidade"] for d in passenger_data]) / total
        avg_timestamp = time.time()
        average_data = {
            "ssid": ssid,
            "average_latitude": avg_lat,
            "average_longitude": avg_lon,
            "average_velocidade": avg_speed,
            "timestamp": avg_timestamp
        }
        try:
            # Atualiza (ou insere) os dados agregados no MongoDB, na coleção 'bus_locations'
            db.bus_locations.update_one(
                {"ssid": ssid},
                {"$set": average_data},
                upsert=True
            )
        except Exception as e:
            return jsonify({"error": str(e)}), 500

        return jsonify({"message": "Atualização processada", "average_data": average_data}), 200
    else:
        return jsonify({"message": "Nenhuma atualização de passageiro recebida"}), 200

if __name__ == '__main__':
    app.run(port=5000, debug=True)
