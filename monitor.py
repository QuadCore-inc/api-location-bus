from pymongo import MongoClient
import time
import os
from datetime import datetime

client = MongoClient("mongodb://localhost:27017")
db = client["transport_data"]

def monitor_changes():
    while True:
        
        os.system('clear' if os.name == 'posix' else 'cls')
        print("🚍 Acompanhando mudanças no MongoDB...\n")
        
        bus_collections = [col for col in db.list_collection_names() if col.startswith("bus_")]
        
        if not bus_collections:
            print("Nenhuma coleção de ônibus encontrada. Verifique se a simulação está em execução.")
            time.sleep(2)
            continue
        
        for collection_name in bus_collections:
            bus_ssid = collection_name.replace("bus_", "")  
            collection = db[collection_name]
            
            users = list(collection.find())
            num_users = len(users)
            
            print(f"🚌 Ônibus: {bus_ssid} | Usuários a bordo: {num_users}")
            
            if num_users > 0:
                print("   👥 Passageiros Ativos:")
                
                for user_doc in users:
                    user_id = user_doc["_id"]
                    final_position = user_doc.get("final_position", {})
                    timestamp = user_doc.get("timestamp", "N/A")
                    user_movimentation = user_doc.get("user_movimentation", {})
                    
                    print(f"     - Usuário: {user_id}")
                    print(f"       📍 Posição Final: {final_position.get('latitude', 'N/A')}, {final_position.get('longitude', 'N/A')}")
                    print(f"       🕒 Última Atualização: {timestamp}")
                    
                
                    print("       Histórico de Movimentação:")
                    for frame_key, frame_data in user_movimentation.items():
                        time_reg = frame_data.get("time", "N/A")
                        lat = frame_data.get("latitude", "N/A")
                        lon = frame_data.get("longitude", "N/A")
                        vel = frame_data.get("velocidade", "N/A")
                        rssi = frame_data.get("RSSI", "N/A")
                        
                        print(f"         {frame_key} -> Time: {time_reg}, Lat: {lat}, Lon: {lon}, Vel: {vel}, RSSI: {rssi}")
                    
                    print()
            
            print("-" * 60)

        time.sleep(2)

if __name__ == "__main__":
    monitor_changes()
