from flask import Flask, request, jsonify
from pymongo import MongoClient
from datetime import datetime

app = Flask(__name__)

client = MongoClient("mongodb://localhost:27017")
db = client["transport_data"]


def get_bus_collection(ssid):

    return db[f"bus_{ssid}"]


def create_or_update_user(bus_ssid, user_id, latitude, longitude, velocidade, rssi, timestamp):

    collection = get_bus_collection(bus_ssid)

    existing_user = collection.find_one({"_id": user_id})
    frame_data = {
        "time": timestamp,
        "latitude": latitude,
        "longitude": longitude,
        "velocidade": velocidade,
        "RSSI": rssi
    }

    if not existing_user:
        
        collection.insert_one({
            "_id": user_id,
            "ssid": bus_ssid,
            "final_position": {
                "latitude": latitude,
                "longitude": longitude
            },
            "timestamp": timestamp,
            "user_movimentation": {
                "time_frame_1": frame_data
            }
        })
    else:

        movement_key = f"time_frame_{len(existing_user['user_movimentation']) + 1}"

        collection.update_one(
            {"_id": user_id},
            {
                "$set": {
                    "final_position": {
                        "latitude": latitude,
                        "longitude": longitude
                    },
                    "timestamp": timestamp,
                    f"user_movimentation.{movement_key}": frame_data
                }
            }
        )


def remove_user(bus_ssid, user_id):

    collection = get_bus_collection(bus_ssid)
    collection.delete_one({"_id": user_id})

@app.route("/api/v1/movements", methods=["POST"])
def create_or_update_movement():

    data = request.get_json()
    if not data:
        return jsonify({"error": "JSON inválido"}), 400

    try:
        bus_ssid = data["bus_ssid"]
        user_id = data["user_id"]
        latitude = data["latitude"]
        longitude = data["longitude"]
        velocidade = data["velocidade"]
        rssi = data["rssi"]
        timestamp = data["timestamp"]  

        create_or_update_user(bus_ssid, user_id, latitude, longitude, velocidade, rssi, timestamp)

        return jsonify({"status": "success"}), 200

    except KeyError as e:
        return jsonify({"error": f"Chave faltando: {e}"}), 400
    except Exception as e:
        return jsonify({"error": str(e)}), 500


@app.route("/api/v1/movements", methods=["DELETE"])
def remove_movement():

    data = request.get_json()
    if not data:
        return jsonify({"error": "JSON inválido"}), 400

    try:
        bus_ssid = data["bus_ssid"]
        user_id = data["user_id"]

        remove_user(bus_ssid, user_id)
        return jsonify({"status": "success"}), 200

    except KeyError as e:
        return jsonify({"error": f"Chave faltando: {e}"}), 400
    except Exception as e:
        return jsonify({"error": str(e)}), 500


if __name__ == "__main__":
    app.run(debug=True, port=5000)
