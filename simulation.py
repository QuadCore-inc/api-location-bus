import random
import time
import threading
from datetime import datetime
from pymongo import MongoClient
import xml.etree.ElementTree as ET
from tqdm import tqdm


def parse_kml(file_path):

    tree = ET.parse(file_path)
    root = tree.getroot()
    namespace = {"kml": "http://www.opengis.net/kml/2.2"}

    coordinates_text = root.find(".//kml:coordinates", namespace).text.strip()
    coord_list = coordinates_text.split()

    route = []
    for coord in coord_list:
        lon_str, lat_str, *_ = coord.split(",")
        lat = float(lat_str)
        lon = float(lon_str)
        route.append({"latitude": lat, "longitude": lon})

    return route

client = MongoClient("mongodb://localhost:27017")
db = client["transport_data"]


def get_bus_collection(ssid):

    return db[f"bus_{ssid}"]


def create_or_update_user(bus_ssid, user_id, latitude, longitude, velocidade, rssi):

    collection = get_bus_collection(bus_ssid)

    
    existing_user = collection.find_one({"_id": user_id})

    
    frame_time = datetime.utcnow().isoformat()
    frame_data = {
        "time": frame_time,
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
            "timestamp": frame_time,
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
                    "timestamp": frame_time,
                    f"user_movimentation.{movement_key}": frame_data
                }
            }
        )


def remove_user(bus_ssid, user_id):

    collection = get_bus_collection(bus_ssid)
    collection.delete_one({"_id": user_id})



def simulate_bus(bus_id, bus_ssid, route):
    route_len = len(route)
    route_index = 0
    min_passenger_time = 60  
    last_passenger_change_time = time.time()

    active_users = []
    current_passengers = 0  


    progress_bar = tqdm(total=route_len, desc=f"🚌 {bus_ssid} em progresso", position=bus_id, leave=False)

    while route_index < route_len:
        current_point = route[route_index]
        base_lat = current_point["latitude"]
        base_lon = current_point["longitude"]

        if time.time() - last_passenger_change_time >= min_passenger_time:
            new_passengers = random.randint(0, 5)

            if new_passengers < current_passengers:
                diff = current_passengers - new_passengers
                for _ in range(diff):
                    user_id_removed = active_users.pop()  
                    remove_user(bus_ssid, user_id_removed)
            elif new_passengers > current_passengers:
                diff = new_passengers - current_passengers
                for i in range(diff):
                    new_user_id = f"user_{current_passengers + i + 1}"
                    active_users.append(new_user_id)

            current_passengers = new_passengers
            last_passenger_change_time = time.time()

        for user_id in active_users:
            lat = round(base_lat + random.uniform(-0.0002, 0.0002), 6)
            lon = round(base_lon + random.uniform(-0.0002, 0.0002), 6)
            velocidade = round(random.uniform(20, 80), 2)
            rssi = random.randint(-90, -40)

            create_or_update_user(bus_ssid, user_id, lat, lon, velocidade, rssi)

        progress_bar.update(1)
        progress_bar.set_postfix(Passageiros=current_passengers)

        route_index += 1
        time.sleep(1) 

    for user_id in active_users:
        remove_user(bus_ssid, user_id)

    progress_bar.close()
    print(f"✅ [{bus_ssid}] Rota concluída! Simulação encerrada.")


if __name__ == "__main__":
    
    kml_file = "rota.kml"
    route_data = parse_kml(kml_file)

    buses = [
        {"bus_id": 1, "ssid": "circular"},
        {"bus_id": 2, "ssid": "SIMA"}
    ]

    threads = []
    for bus in buses:
        t = threading.Thread(target=simulate_bus, args=(bus["bus_id"], bus["ssid"], route_data))
        threads.append(t)
        t.start()

    for t in threads:
        t.join()

    print("🚦 Todas as simulações foram concluídas!")
