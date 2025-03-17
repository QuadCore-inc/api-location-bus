from flask import Flask, request, jsonify
from pymongo import MongoClient
from datetime import datetime
import json
import xml.etree.ElementTree as ET
import time
import pytz

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

connection_string = "mongodb+srv://QuadCore:AViuL9s9QSgkCBX7@buson.rhgqz.mongodb.net/transport_data?retryWrites=true&w=majority"
client = MongoClient(connection_string)
db = client["BusON_Crowdsourcing"]


def format_bus_document(ssid):
    splited_bus_ssid = ssid.split("/")
    
    bus_line = f"line_{splited_bus_ssid[0]}"
    bus_id = f"bus_{splited_bus_ssid[1]}"
    document_id = f"{bus_line}/{bus_id}"
    return db["buses_locations"], document_id, bus_line, bus_id, ssid


def get_brazil_timestamp():
    brasil_tz = pytz.timezone("America/Sao_Paulo")
    return datetime.now(brasil_tz).strftime('%Y-%m-%d %H:%M:%S %z')

def create_or_update_bus(bus_ssid, latitude, longitude, speed, rssi, heading, timestamp):
    collection, document_id, bus_line, bus_id, ssid = format_bus_document(bus_ssid)

    existing_bus = collection.find_one({"_id": document_id})
    frame_data = {
        "time": timestamp,
        "latitude": latitude,
        "longitude": longitude,
        "speed": speed,
        "RSSI": rssi,
        "heading": heading
    }

    if not existing_bus:
        collection.insert_one({
            "_id": document_id,
            "bus_line": bus_line,
            "bus_id": bus_id,
            "ssid": ssid,
            "last_update": frame_data,
            "user_movimentation": {
                "time_frame_1": frame_data
            }
        })
    else:
        movement_key = f"time_frame_{len(existing_bus['user_movimentation']) + 1}"
        collection.update_one(
            {"_id": document_id},
            {
                "$set": {
                    "last_update": frame_data,
                    f"user_movimentation.{movement_key}": frame_data
                }
            }
        )


def remove_bus(bus_ssid):
    db["buses_locations"].delete_one({"_id": bus_ssid})

def main():
    bus_ssid = "circular_ufpa/circular"
    remove_bus(bus_ssid)
    time.sleep(1)
    while True:
        for timestep in range(len(coords_list)):
            coord = coords_list[timestep]
            print(f"Sending new location {coord} of ssid {bus_ssid}")
            create_or_update_bus(bus_ssid, coord[2], coord[1], 0, 0, 0, timestep)
            time.sleep(1)


if __name__ == "__main__":
    main()
