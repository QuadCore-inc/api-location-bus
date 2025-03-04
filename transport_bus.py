import random
import time
import threading
from datetime import datetime
from pymongo import MongoClient
import xml.etree.ElementTree as ET
from tqdm import tqdm  

client = MongoClient("mongodb://localhost:27017")
db = client["transport_data"]
buses_collection = db["buses"]

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

def update_bus_document(bus_id, bus_ssid, base_lat, base_lon, num_passengers):

    if num_passengers == 0:
        buses_collection.update_one(
            {"_id": bus_id},
            {
                "$set": {
                    "ssid": bus_ssid,
                    "passageiros": 0
                },
                "$unset": {"usuarios": ""}
            },
            upsert=True
        )
    else:
        usuarios_subdocs = {}
        
        for i in range(1, num_passengers + 1):
            user_id = f"user_{i}"
            lat = round(base_lat + random.uniform(-0.0002, 0.0002), 6)
            lon = round(base_lon + random.uniform(-0.0002, 0.0002), 6)
            velocidade = round(random.uniform(20, 80), 2)
            rssi = random.randint(-90, -40)
            timestamp = datetime.utcnow().isoformat()
            
            usuarios_subdocs[user_id] = {
                "latitude": lat,
                "longitude": lon,
                "velocidade": velocidade,
                "RSSI": rssi,
                "timestamp": timestamp
            }
        
        buses_collection.update_one(
            {"_id": bus_id},
            {
                "$set": {
                    "ssid": bus_ssid,
                    "passageiros": num_passengers,
                    "usuarios": usuarios_subdocs
                }
            },
            upsert=True
        )
        
def simulate_bus(bus_id, bus_ssid, route):

    route_len = len(route)
    route_index = 0
    min_passenger_time = 60  
    last_passenger_change_time = time.time()  

    # Inicializa a quantidade de pass
    num_passengers = random.randint(0, 5)

    # Criando barra de progresso para esse ônibus
    progress_bar = tqdm(total=route_len, desc=f"🛣️ {bus_ssid} em progresso", position=bus_id, leave=False)

    while route_index < route_len:
        current_point = route[route_index]
        base_lat = current_point["latitude"]
        base_lon = current_point["longitude"]
        
        # Se passou mais de 1 minuto desde a última mudança, podemos alterar o número de passageiros
        if time.time() - last_passenger_change_time >= min_passenger_time:
            num_passengers = random.randint(0, 5)  # Nova quantidade de passageiros
            last_passenger_change_time = time.time()  # Atualiza o tempo da última alteração
        
        update_bus_document(bus_id, bus_ssid, base_lat, base_lon, num_passengers)
        
        # Atualiza a barra de progresso
        progress_bar.update(1)
        progress_bar.set_postfix(Passageiros=num_passengers)
        
        route_index += 1
        time.sleep(1)

    # Finaliza a barra de progresso e exibe conclusão
    progress_bar.close()
    print(f"✅ [{bus_ssid}] Rota concluída! Simulação encerrada.")

##############################
# 5) Rotina principal
##############################
if __name__ == "__main__":
    # Lê o arquivo KML da rota
    kml_file = "rota.kml"
    route_data = parse_kml(kml_file)
    
    # Criamos os 3 ônibus com suas respectivas threads
    buses = [
        {"bus_id": 1, "ssid": "circular"},
        {"bus_id": 2, "ssid": "SIMA"},
        {"bus_id": 3, "ssid": "circulinho"}
    ]
    
    threads = []
    for bus in buses:
        t = threading.Thread(target=simulate_bus, args=(bus["bus_id"], bus["ssid"], route_data))
        threads.append(t)
        t.start()
    
    for t in threads:
        t.join()
    
    print("🚦 Todas as simulações foram concluídas!")
