from pymongo import MongoClient
import time

# Conexão com MongoDB
connection_string = "mongodb+srv://QuadCore:AViuL9s9QSgkCBX7@buson.rhgqz.mongodb.net/transport_data?retryWrites=true&w=majority"
client = MongoClient(connection_string)
db = client["BusON_Crowdsourcing"]
collection = "buses_locations"

# Função para criar ou atualizar a localização do ônibus
def create_or_update_bus(bus_ssid, latitude, longitude, speed, heading, timestamp):
    buses_locations_collection = db["buses_locations"]
    
    # Recuperando o documento com o nome da coleção (o ssid do ônibus)
    existing_bus = buses_locations_collection.find_one({"_id": bus_ssid})
    
    # Dados do movimento
    frame_data = {
        "time": timestamp,
        "latitude": latitude,
        "longitude": longitude,
        "speed": speed,  # Substituído 'velocidade' por 'speed'
        "heading": heading,  # Adicionando o campo 'heading'
    }

    if not existing_bus:
        # Caso o documento não exista, cria um novo
        buses_locations_collection.insert_one({
            "_id": bus_ssid,
            "last_update": {
                "time": timestamp,
                "latitude": latitude,
                "longitude": longitude,
                "speed": speed,  
                "heading": heading,  
            },
            "bus_movimentation": {
                "time_frame_1": frame_data
            }
        })
    else:
        # Caso o documento já exista, atualiza a localização
        movement_key = f"time_frame_{len(existing_bus['bus_movimentation']) + 1}"

        buses_locations_collection.update_one(
            {"_id": bus_ssid},
            {
                "$set": {
                    "last_update": {
                        "time": timestamp,
                        "latitude": latitude,
                        "longitude": longitude,
                        "speed": speed,  
                        "heading": heading, 
                        
                    },
                    f"bus_movimentation.{movement_key}": frame_data
                }
            }
        )

# Função para remover o usuário (se necessário)
def remove_bus(bus_ssid):
    db[collection].delete_one({"_id": bus_ssid})

# Função principal que executa o código periodicamente
def main():
    # Exemplo de remoção de um bus (caso seja necessário)
    bus_ssid = "bus_circulinho"
    remove_bus(bus_ssid)
    time.sleep(2)
    
    bus_collection = bus_ssid
    print(f"Iniciando atualizações do ônibus {bus_ssid}")
    
    while True:
        bus_data = db[bus_collection].find_one({"_id": "user_kauan"})
        if bus_data and "last_update" in bus_data:
            latitude = bus_data["last_update"]["latitude"]
            longitude = bus_data["last_update"]["longitude"]
            speed = bus_data["last_update"]["speed"]
            heading = bus_data["last_update"]["heading"]  # Incluindo o 'heading'
            timestamp = time.strftime('%Y-%m-%d %H:%M:%S %z', time.localtime())  # Formato: '2025-03-14 14:25:30 +0000'
            
            # Atualiza a coleção "buses_locations" com os dados obtidos
            create_or_update_bus(bus_collection, latitude, longitude, speed, heading, timestamp)
            print(f"Updated bus location for {bus_ssid}: {latitude}, {longitude} at {timestamp}")
        
        # Delay de 1 segundo entre as consultas e atualizações
        time.sleep(1)

if __name__ == "__main__":
    main()
