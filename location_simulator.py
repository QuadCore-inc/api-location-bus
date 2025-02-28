import requests
import time
import random
import threading

# URL da API do Calculator (deve estar ativa para receber as atualizações)
API_URL = "http://127.0.0.1:5000/update"

def simulate_bus1():
    """
    Ônibus 1: possui vários passageiros (n = 5, por exemplo).
    Cada passageiro envia sua localização (com pequenas variações, simulando que estão no mesmo veículo)
    a cada 1 segundo.
    """
    n = 5
    bus_ssid = "onibus_1"
    base_lat = -1.45502
    base_lon = -48.5024

    while True:
        for i in range(n):
            passenger_id = f"bus1_passenger_{i+1}"
            lat = base_lat + random.uniform(-0.0005, 0.0005)
            lon = base_lon + random.uniform(-0.0005, 0.0005)
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
                # print(f"[Bus 1] {passenger_id} -> {response.text}")
            except Exception as e:
                print(f"[Bus 1] Erro ao enviar update do {passenger_id}: {e}")
        time.sleep(1)

def simulate_bus2():
    """
    Ônibus 2: possui um único passageiro que envia atualizações a cada 1 segundo.
    """
    bus_ssid = "onibus_2"
    base_lat = -1.45600
    base_lon = -48.50300
    passenger_id = "bus2_passenger_1"

    while True:
        lat = base_lat + random.uniform(-0.005, 0.005)
        lon = base_lon + random.uniform(-0.005, 0.005)
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
            # print(f"[Bus 2] {passenger_id} -> {response.text}")
        except Exception as e:
            print(f"[Bus 2] Erro: {e}")
        time.sleep(1)

def simulate_bus3():
    """
    Ônibus 3: possui um passageiro que envia atualização apenas a cada 5 segundos.
    Nos intervalos, nenhum dado é enviado, mantendo a última localização registrada.
    """
    bus_ssid = "onibus_3"
    base_lat = -1.45700
    base_lon = -48.50400
    passenger_id = "bus3_passenger_1"

    while True:
        lat = base_lat + random.uniform(-0.005, 0.005)
        lon = base_lon + random.uniform(-0.005, 0.005)
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
            # print(f"[Bus 3] {passenger_id} -> {response.text}")
        except Exception as e:
            print(f"[Bus 3] Erro: {e}")
        time.sleep(5)

if __name__ == "__main__":
    # Executa as simulações em threads separadas
    t1 = threading.Thread(target=simulate_bus1)
    t2 = threading.Thread(target=simulate_bus2)
    t3 = threading.Thread(target=simulate_bus3)

    t1.start()
    t2.start()
    t3.start()

    t1.join()
    t2.join()
    t3.join()
