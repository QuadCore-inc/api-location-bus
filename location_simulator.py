import requests
import time
import random
import threading
import xml.etree.ElementTree as ET

API_URL = "http://127.0.0.1:5000/update"

def parse_kml(file_path):
    """
    Faz o parsing de um arquivo KML para extrair a rota.
    Retorna uma lista de dicionários com 'latitude' e 'longitude'.
    """
    tree = ET.parse(file_path)
    root = tree.getroot()
    # Define o namespace do KML
    namespace = {"kml": "http://www.opengis.net/kml/2.2"}
    # Localiza o elemento <coordinates>
    coordinates_text = root.find(".//kml:coordinates", namespace).text.strip()
    # Separa as coordenadas; cada item tem o formato "longitude,latitude,altitude"
    coord_list = coordinates_text.split()
    route = []
    for coord in coord_list:
        parts = coord.split(",")
        lon = float(parts[0])
        lat = float(parts[1])
        route.append({"latitude": lat, "longitude": lon})
    return route

# Carrega a rota a partir do arquivo KML
ROUTE = parse_kml("rota.kml")

def simulate_bus1():
    """
    Ônibus 1: simula vários passageiros (ex: n = 5) que viajam juntos
    ao longo da rota. Cada passageiro tem um pequeno ruído para simular
    pequenas diferenças nas localizações.
    """
    n = 5
    bus_ssid = "onibus_1"
    route_index = 0
    route_len = len(ROUTE)

    while True:
        base_point = ROUTE[route_index]
        for i in range(n):
            passenger_id = f"bus1_passenger_{i+1}"
            # Adiciona ruído pequeno para simular variações individuais
            lat = base_point["latitude"] + random.uniform(-0.0002, 0.0002)
            lon = base_point["longitude"] + random.uniform(-0.0002, 0.0002)
            speed = random.uniform(0, 80)
            timestamp = time.time()
            data = {
                "ssid": bus_ssid,
                "passenger_id": passenger_id,
                "latitude": lat,
                "longitude": lon,
                "velocidade": speed,
                "timestamp": timestamp
            }
            try:
                response = requests.post(API_URL, json=data)
                #print(f"[Bus 1] {passenger_id} -> {response.text}")
            except Exception as e:
                print(f"[Bus 1] Erro ao enviar update do {passenger_id}: {e}")
        # Avança para o próximo ponto da rota (loop infinito)
        route_index = (route_index + 1) % route_len
        time.sleep(1)

def simulate_bus2():
    """
    Ônibus 2: simula um único passageiro que segue os pontos da rota.
    A cada 1 segundo, envia a localização exata do ponto atual.
    """
    bus_ssid = "onibus_2"
    route_index = 0
    route_len = len(ROUTE)
    while True:
        base_point = ROUTE[route_index]
        passenger_id = "bus2_passenger_1"
        lat = base_point["latitude"]
        lon = base_point["longitude"]
        speed = random.uniform(0, 80)
        timestamp = time.time()
        data = {
            "ssid": bus_ssid,
            "passenger_id": passenger_id,
            "latitude": lat,
            "longitude": lon,
            "velocidade": speed,
            "timestamp": timestamp
        }
        try:
            response = requests.post(API_URL, json=data)
            #print(f"[Bus 2] {passenger_id} -> {response.text}")
        except Exception as e:
            print(f"[Bus 2] Erro: {e}")
        route_index = (route_index + 1) % route_len
        time.sleep(1)

def simulate_bus3():
    """
    Ônibus 3: simula um passageiro que envia a localização a cada 5 segundos,
    seguindo os pontos da rota. Nos intervalos, nenhum dado é enviado, mantendo
    a última posição registrada.
    """
    bus_ssid = "onibus_3"
    route_index = 0
    route_len = len(ROUTE)
    while True:
        base_point = ROUTE[route_index]
        passenger_id = "bus3_passenger_1"
        lat = base_point["latitude"]
        lon = base_point["longitude"]
        speed = random.uniform(0, 80)
        timestamp = time.time()
        data = {
            "ssid": bus_ssid,
            "passenger_id": passenger_id,
            "latitude": lat,
            "longitude": lon,
            "velocidade": speed,
            "timestamp": timestamp
        }
        try:
            response = requests.post(API_URL, json=data)
            #print(f"[Bus 3] {passenger_id} -> {response.text}")
        except Exception as e:
            print(f"[Bus 3] Erro: {e}")
        route_index = (route_index + 1) % route_len
        time.sleep(5)

if __name__ == "__main__":
    # Executa as simulações de cada ônibus em threads separadas
    t1 = threading.Thread(target=simulate_bus1)
    t2 = threading.Thread(target=simulate_bus2)
    t3 = threading.Thread(target=simulate_bus3)

    t1.start()
    t2.start()
    t3.start()

    t1.join()
    t2.join()
    t3.join()
