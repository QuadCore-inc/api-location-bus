import random
import time
import threading
import requests  
from datetime import datetime
import xml.etree.ElementTree as ET
from tqdm import tqdm
from constants import API_HOST
import math

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

def create_or_update_user_via_api(bus_ssid, user_id, latitude, longitude, velocidade, rssi):

    url = F"https://buson-api-websocket-1.onrender.com/api/v1/movements"  # <-- Ajuste conforme a rota e porta da sua API
    payload = {
        "bus_ssid": bus_ssid,
        "user_id": user_id,
        "latitude": latitude,
        "longitude": longitude,
        "speed": velocidade,
        "rssi": rssi,
        "heading": 0,
        "timestamp": datetime.utcnow().isoformat()
    }
    try:
        response = requests.post(url, json=payload, timeout=5)
        response.raise_for_status()
    except requests.RequestException as e:
        print(f"[ERRO] Falha ao enviar dados para a API: {e}")

def remove_user_via_api(bus_ssid, user_id):

    url = f"https://buson-api-websocket-1.onrender.com/api/v1/movements"  
    payload = {
        "bus_ssid": bus_ssid,
        "user_id": user_id
    }
    try:
        response = requests.delete(url, json=payload, timeout=5)
        response.raise_for_status()
    except requests.RequestException as e:
        print(f"[ERRO] Falha ao remover usuário na API: {e}")
        
def generate_nearby_location(base_lat, base_lon, radius_meters=10):
    # Fator de conversão aproximado: 1 grau de latitude ≈ 111.32 km (111320 metros)
    meters_per_degree = 111320

    # Converter metros para graus
    delta_lat = (random.gauss(0, 1) * radius_meters) / meters_per_degree
    delta_lon = (random.gauss(0, 1) * radius_meters) / (meters_per_degree * math.cos(math.radians(base_lat)))

    # Gerar nova localização dentro do raio
    lat = round(base_lat + delta_lat, 10)
    lon = round(base_lon + delta_lon, 10)

    return lat, lon


def simulate_bus(bus_id, bus_ssid, route):

    route_len = len(route)
    route_index = 0
    min_passenger_time = 10  
    last_passenger_change_time = time.time()

    active_users = []
    current_passengers = 0

    progress_bar = tqdm(total=route_len, desc=f"🚌 {bus_ssid} em progresso", position=bus_id, leave=False)

    while route_index < route_len:
        current_point = route[route_index]
        base_lat = current_point["latitude"]
        base_lon = current_point["longitude"]

        if time.time() - last_passenger_change_time >= min_passenger_time:
            new_passengers = random.randint(1, 20)

            if new_passengers < current_passengers:
                diff = current_passengers - new_passengers
                for _ in range(diff):
                    if active_users:
                        user_id_removed = active_users.pop()  
                        remove_user_via_api(bus_ssid, user_id_removed)
            elif new_passengers > current_passengers:
                diff = new_passengers - current_passengers
                for i in range(diff):
                    new_user_id = f"user_{current_passengers + i + 1}"
                    active_users.append(new_user_id)

            current_passengers = new_passengers
            last_passenger_change_time = time.time()

        for user_id in active_users:
            new_lat, new_lon = generate_nearby_location(base_lat, base_lon)
            velocidade = round(random.uniform(10, 20), 2)
            rssi = random.randint(-90, -40)

            create_or_update_user_via_api(bus_ssid, user_id, new_lat, new_lon, velocidade, rssi)

        progress_bar.update(1)
        progress_bar.set_postfix(Passageiros=current_passengers)

        route_index += 1
        time.sleep(1)  

    for user_id in active_users:
        remove_user_via_api(bus_ssid, user_id)

    progress_bar.close()
    print(f"✅ [{bus_ssid}] Rota concluída! Simulação encerrada.")

if __name__ == "__main__":

    kml_file = "rota.kml"
    route_data = parse_kml(kml_file)

    buses = [
        {"bus_id": 1, "ssid": "circular_ufpa/sima"},
        # {"bus_id": 2, "ssid": "circular_ufpa/sima"}
    ]

    threads = []
    for bus in buses:
        t = threading.Thread(target=simulate_bus, args=(bus["bus_id"], bus["ssid"], route_data))
        threads.append(t)
        t.start()

    for t in threads:
        t.join()

    print("🚦 Todas as simulações foram concluídas!")
