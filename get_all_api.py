from flask import Flask, request, jsonify
from pymongo import MongoClient

app = Flask(__name__)

client = MongoClient("mongodb://localhost:27017")
db = client["transport_data"]
buses_collection = db["buses"]

@app.route("/receive_data", methods=["POST"])
def receive_data():

    data = request.get_json()

    if not data:
        return jsonify({"error": "Dados inválidos"}), 400

    bus_id = data["bus_id"]
    buses_collection.update_one(
        {"_id": bus_id},
        {"$set": data},
        upsert=True
    )

    return jsonify({"message": "Dados recebidos com sucesso"}), 200

if __name__ == "__main__":
    app.run(debug=True, port=5000)
