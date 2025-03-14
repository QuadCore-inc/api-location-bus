from flask import Flask, request, jsonify
from pymongo import MongoClient
from datetime import datetime
import json
import xml.etree.ElementTree as ET
import time

# Caminho do arquivo KML
arquivo_kml = "rota.kml"

# Carregar e processar o arquivo KML
tree = ET.parse(arquivo_kml)
root = tree.getroot()
namespace = {'kml': 'http://www.opengis.net/kml/2.2'}

coords_list = []

# Extrair coordenadas do KML
for linestring in root.findall(".//{http://www.opengis.net/kml/2.2}LineString/{http://www.opengis.net/kml/2.2}coordinates"):
    coordenadas_texto = linestring.text.strip()
    coordenadas = [tuple(map(float, coord.split(','))) for coord in coordenadas_texto.split()]
    coords_list.extend(coordenadas)
    coords_list = [[time, coord[0], coord[1]] for time, coord in enumerate(coords_list)]

client = MongoClient("mongodb://localhost:27017")
db = client["transport_data"]
collection = "buses_locations"


def create_or_update_bus(bus_ssid, latitude, longitude, timestamp):


    existing_user = db[collection].find_one({"_id": bus_ssid})
    frame_data = {
        "time": timestamp,
        "latitude": latitude,
        "longitude": longitude,
    }

    if not existing_user:
        
        db[collection].insert_one({
            "_id": bus_ssid,
            "last_update": {
                "latitude": latitude,
                "longitude": longitude,
                "time": timestamp
            },
            "timestamp": timestamp,
            "bus_movimentation": {
                "time_frame_1": frame_data
            }
        })
    else:

        movement_key = f"time_frame_{len(existing_user['bus_movimentation']) + 1}"

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
    time.sleep(2)
    while True:
        for timestep in range(len(coords_list)):
            coord = coords_list[timestep]
            print(f"Sending new location! {coord}")
            create_or_update_bus("bus_sima", coord[2], coord[1], timestep)
            time.sleep(1)


if __name__ == "__main__":
    main()
