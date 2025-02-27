# monitor.py

import asyncio
import requests
import time

API_URL = "http://127.0.0.1:5000/localizacao"
SSIDS_FIXOS = [f"onibus_{i}" for i in range(1, 11)]

def escolher_ssid():
    print("\n Dispositivos disponíveis para monitoramento:")
    for i, ssid in enumerate(SSIDS_FIXOS, 1):
        print(f"{i}. {ssid}")
    
    while True:
        try:
            escolha = int(input("\nDigite o número do dispositivo que deseja monitorar: "))
            if 1 <= escolha <= 10:
                return SSIDS_FIXOS[escolha - 1]
            else:
                print(" Escolha um número entre 1 e 10.")
        except ValueError:
            print("Entrada inválida. Digite um número válido.")

async def monitorar_localizacao(ssid):
    print(f"\n Monitorando a localização de {ssid} em tempo real...\n")
    while True:
        try:
            response = requests.get(f"{API_URL}/{ssid}")
            if response.status_code == 200:
                localizacao = response.json()
                print(f"\r Localização atual de {ssid}: {localizacao}", end="", flush=True)
            else:
                print(f"\n {response.json().get('erro', 'Erro desconhecido')}")
        except Exception as e:
            print(f"\n Erro ao obter a localização: {e}")

        time.sleep(1)  

async def main():
    ssid_escolhido = escolher_ssid()
    await monitorar_localizacao(ssid_escolhido)

if __name__ == "__main__":
    asyncio.run(main())