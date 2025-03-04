import random
import time
import threading
import requests
import xml.etree.ElementTree as ET
from tqdm import tqdm  

API_URL = "http://127.0.0.1:5000/receive_data"

tqdm_lock = threading.Lock()

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

def generate_bus_data(bus_id, bus_ssid, base_lat, base_lon, num_passengers):

    bus_data = {
        "bus_id": bus_id,
        "ssid": bus_ssid,
        "passageiros": num_passengers,
        "usuarios": {}
    }

    if num_passengers > 0:
        for i in range(1, num_passengers + 1):
            user_id = f"user_{i}"
            lat = round(base_lat + random.uniform(-0.0002, 0.0002), 6)
            lon = round(base_lon + random.uniform(-0.0002, 0.0002), 6)
            velocidade = round(random.uniform(20, 80), 2)
            rssi = random.randint(-90, -40)
            timestamp = time.time()

            bus_data["usuarios"][user_id] = {
                "latitude": lat,
                "longitude": lon,
                "velocidade": velocidade,
                "RSSI": rssi,
                "timestamp": timestamp
            }
    
    return bus_data

def simulate_bus(bus_id, bus_ssid, route, position):

    route_len = len(route)
    route_index = 0
    min_passenger_time = 60  
    last_passenger_change_time = time.time()  

    num_passengers = random.randint(0, 5)

    with tqdm_lock:
        progress_bar = tqdm(
            total=route_len, 
            desc=f"🛣️   {bus_ssid} em progresso", 
            position=position,
            dynamic_ncols=True
        )

    while route_index < route_len:
        current_point = route[route_index]
        base_lat = current_point["latitude"]
        base_lon = current_point["longitude"]
        
        if time.time() - last_passenger_change_time >= min_passenger_time:
            num_passengers = random.randint(0, 5)  
            last_passenger_change_time = time.time()
        
        bus_data = generate_bus_data(bus_id, bus_ssid, base_lat, base_lon, num_passengers)
        
        try:
            requests.post(API_URL, json=bus_data)
        except requests.exceptions.RequestException:
            pass 

        with tqdm_lock:
            progress_bar.update(1)
            progress_bar.set_postfix(Passageiros=num_passengers)
        
        route_index += 1
        time.sleep(1)

    with tqdm_lock:
        progress_bar.close() 

if __name__ == "__main__":
    kml_file = "rota.kml"
    route_data = parse_kml(kml_file)
    
    buses = [
        {"bus_id": 1, "ssid": "circular"},
        {"bus_id": 2, "ssid": "SIMA"},
        {"bus_id": 3, "ssid": "circulinho"}
    ]
    
    threads = []
    for index, bus in enumerate(buses):
        t = threading.Thread(target=simulate_bus, args=(bus["bus_id"], bus["ssid"], route_data, index))
        threads.append(t)
        t.start()
    
    for t in threads:
        t.join()
    
    print("🚦 Todas as simulações foram concluídas!")
