#simulador_location.py


import asyncio
import random
import json
import requests

API_URL = "http://127.0.0.1:5000/localizacao"

SSIDS_FIXOS = [f"onibus_{i}" for i in range(1, 11)] 



async def atualizar_localizacoes():
    while True:
        for ssid in SSIDS_FIXOS:
            location_data = {
                "ssid": ssid,
                "longitude": -48.5024 + random.uniform(-0.005, 0.005),
                "latitude": -1.45502 + random.uniform(-0.005, 0.005),
                "velocidade": random.uniform(0, 100),
                "timestamp": asyncio.get_event_loop().time()
            }

            try:
                response = requests.post(API_URL, json=location_data)
                print(f"Atualizando {ssid}: {location_data} -> Resposta: {response.json()}")
            except Exception as e:
                print(f"Erro ao atualizar {ssid}: {e}")

            await asyncio.sleep(1) 

        print("\n--- Todas as localizações foram atualizadas. Reiniciando ciclo... ---\n")
        await asyncio.sleep(2)

async def main():
    print("Iniciando atualização contínua das localizações...")
    await atualizar_localizacoes()

asyncio.run(main())