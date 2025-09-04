from flask import Flask, jsonify, request
import logging
from smart_objects.model.plant_descriptor import PlantDescriptor
from process.client_data_collector import PlantClient
from smart_objects.resourses.factory_plants import PlantFactory

app = Flask(__name__)

logging.basicConfig(level=logging.INFO)

app.plants = PlantFactory.create_plants_from_json("smart_objects/resourses/plants_config.json")
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

if __name__ == "__main__":
    # Avvia il server Flask
    app.run(host="0.0.0.0", port=5000)