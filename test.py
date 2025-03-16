from pymongo import MongoClient
from datetime import datetime
import xml.etree.ElementTree as ET
import time

client = MongoClient("mongodb://localhost:27017")
db = client["transport_data"]
collection = 'buses_locations'

# Caminho do arquivo KML
arquivo_kml = "rota.kml"

# Carregar e processar o arquivo KML
tree = ET.parse(arquivo_kml)s
root = tree.getroot()
namespace = {'kml': 'http://www.opengis.net/kml/2.2'}

coords_list = []

for linestring in root.findall(".//{http://www.opengis.net/kml/2.2}LineString/{http://www.opengis.net/kml/2.2}coordinates"):
    coordenadas_texto = linestring.text.strip()
    coordenadas = [tuple(map(float, coord.split(','))) for coord in coordenadas_texto.split()]
    coords_list.extend(coordenadas)
    coords_list = [[coords[0], coords[1], timestep] for timestep, coords in enumerate(coords_list)]
    
def create_and_update_bus(bus_ssid, latitude, longitude, timestamp):
    existing_bus = db[collection].find_one({"_id": bus_ssid})
    frame_data = {
        "time": timestamp,
        "latitude": latitude,
        "longitude": longitude,
    }

    if not existing_bus:
        
        db[collection].insert_one({
            "_id": bus_ssid,
            "last_update": {
                "latitude": latitude,
                "longitude": longitude,
                "time": timestamp,
            },
            "bus_movimentation": {
                "time_frame_1": frame_data
            }
        })
    else:
        movement_key = f"time_frame_{len(existing_bus['bus_movimentation']) + 1}"
        db[collection].update_one(
            {"_id": bus_ssid},
            {
                "$set": {
                    "last_update": {
                        "latitude": latitude,
                        "longitude": longitude,
                        "time": timestamp
                    },
                    f"bus_movimentation.{movement_key}": frame_data
                }
            }
        )

def remove_user(bus_ssid):
    db[collection].delete_one({"_id": bus_ssid})

def main():
    remove_user("bus_sima")
    while True:
        for timestep, coord in enumerate(coords_list):
            print(f"New location received in time {timestep}! Updating MongoDB with coords({coord[0], coord[1]})")
            create_and_update_bus("bus_sima", coord[1], coord[0], timestep)
            time.sleep(2)
    
if __name__ == "__main__":
    main()
