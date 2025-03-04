from pymongo import MongoClient
import time
import os

client = MongoClient("mongodb://localhost:27017")
db = client["transport_data"]
buses_collection = db["buses"]

def monitor_changes():

    while True:
        os.system('clear' if os.name == 'posix' else 'cls')
        print("🚍 Acompanhando mudanças no MongoDB...\n")

        buses = buses_collection.find()

        for bus in buses:
            print(f"🚌 Ônibus: {bus['ssid']} | Passageiros: {bus['passageiros']}")
            
            if bus["passageiros"] > 0:
                print("   👥 Passageiros:")
                for user_id, user_data in bus["usuarios"].items():
                    print(f"     - {user_id}:")
                    print(f"       🌍 Localização: {user_data['latitude']}, {user_data['longitude']}")
                    print(f"       ⚡ Velocidade: {user_data['velocidade']} km/h")
                    print(f"       📶 RSSI: {user_data['RSSI']} dBm")
                    print(f"       🕒 Timestamp: {user_data['timestamp']}\n")
            
            print("-" * 60)  
        
        time.sleep(2) 

if __name__ == "__main__":
    monitor_changes()
