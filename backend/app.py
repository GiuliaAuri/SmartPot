from flask import Flask, jsonify, request
from flask_socketio import SocketIO, emit
import logging
import sys
import os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from plants_system.smart_objects.models.plant_descriptor import PlantDescriptor
from plants_system.process.client_data_collector import PlantClient
from plants_system.smart_objects.resources.factory_plants import PlantFactory


app = Flask(__name__)
socketio = SocketIO(app, cors_allowed_origins="*")

logging.basicConfig(level=logging.INFO)

app.plants = PlantFactory.create_plants_from_json("plants_system/smart_objects/resources/plants_config.json")
app.client = PlantClient(app.plants)

@app.route('/api/plants/<plant_id>/telemetry', methods=['GET'])
def get_plant_telemetry(plant_id):
    # use app.plants which tests may initialize when importing this module
    plant : PlantDescriptor = next((p for p in app.plants if p.plant_id == plant_id), None)
    if not plant:
        return {"error": "Plant not found"}, 404
    telemetry_data = {}
    for sensor in plant.sensors:
        telemetry_data[sensor.device] = {
            "type": sensor.type,
            "value": sensor.value,
            "unit": sensor.unit
        }
    return jsonify({"plant_id": plant_id, "telemetry": telemetry_data}), 200

@app.route('/api/plants/<plant_id>/actuators/<actuator_name>/command', methods=['POST'])
def post_actuator_command(plant_id, actuator_name):
    plant : PlantDescriptor = next((p for p in app.plants if p.plant_id == plant_id), None)
    if not plant:
        return {"error": "Plant not found"}, 404

    actuator = next((a for a in plant.actuators if a.device == actuator_name), None)
    if not actuator:
        return {"error": "Actuator not found"}, 404

    command = request.json.get("command")
    logging.info(f"Received command for {actuator_name} of plant {plant_id}: {command}")
    if not command:
        return {"error": "No command provided"}, 400

    app.client.send_command(plant_id, actuator_name, command)
    return {"status": actuator.status, "plant_id": plant_id, "actuator": actuator_name, "command": command}, 200

@app.route('/api/plants', methods=['GET'])
def get_all_plants():
    return jsonify([p.plant_id for p in app.plants])

@app.route('/api/plants/telemetry', methods=['GET'])
def get_all_telemetry():
    result = []
    for plant in app.plants:
        telemetry_data = {}
        for sensor in plant.sensors:
            telemetry_data[sensor.device] = {
                "type": sensor.type,
                "value": sensor.value,
                "unit": sensor.unit
            }
        result.append({
            "plant_id": plant.plant_id,
            "telemetry": telemetry_data
        })
    return jsonify(result),200

def notify_telemetry_update(plant_id, telemetry_data):
    socketio.emit('telemetry_update', {'plant_id': plant_id, 'telemetry': telemetry_data})

def check_watering_status(plant):
    """Check if plant is currently watering"""
    for actuator in plant.actuators:
        if actuator.device == "irrigation_actuator":
            return actuator.status.upper() == "ON"
    return False

if __name__ == "__main__":
    socketio.run(app, host="127.0.0.1", port=5000)

"""
da aggiungere nella parte di front-end
import { io } from "socket.io-client";

const socket = io("http://127.0.0.1:5000"); // Cambia con l'URL del backend

socket.on("connect", () => {
  console.log("WebSocket connesso!");
});

socket.on("telemetry_update", (data) => {
  console.log("Dati aggiornati:", data);
  // Aggiorna la UI con i nuovi dati
});"""