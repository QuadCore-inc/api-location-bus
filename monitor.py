import pymongo
import time

def main():
    # Conecta ao MongoDB (banco 'crowdsourcing')
    client = pymongo.MongoClient("mongodb://localhost:27017/")
    db = client.crowdsourcing
    collection = db.bus_locations

    # Menu para o usuário escolher qual ônibus monitorar
    print("Escolha o ônibus para monitorar:")
    print("1 - onibus_1")
    print("2 - onibus_2")
    print("3 - onibus_3")

    choice = None
    while choice not in ['1', '2', '3']:
        choice = input("Digite 1, 2 ou 3: ").strip()
    ssid = f"onibus_{choice}"
    print(f"Monitorando {ssid}...\n")

    # Consulta contínua ao MongoDB a cada 1 segundo para exibir a localização atual do ônibus
    while True:
        doc = collection.find_one({"ssid": ssid}, {"_id": 0})
        if doc:
            print(f"Localização agregada de {ssid}: {doc}")
        else:
            print(f"Nenhum dado disponível para {ssid}.")
        time.sleep(1)

if __name__ == "__main__":
    main()
