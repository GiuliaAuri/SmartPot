import sys
import os

# Aggiungi la root del progetto al sys.path
PROJECT_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
if PROJECT_ROOT not in sys.path:
    sys.path.insert(0, PROJECT_ROOT)

from flask import Flask, jsonify, request
import logging
from flask_cors import CORS
from plants_system.smart_objects.models.plant_descriptor import PlantDescriptor
from plants_system.process.data_collector_main import Main
from plants_system.smart_objects.resources.factory_plants import PlantFactory
from plants_system.process.policy_manager import PolicyManager

app = Flask(__name__)
CORS(app)  # Enable CORS for all routes

logging.basicConfig(level=logging.INFO)
FILENAME = os.path.abspath(os.path.join(PROJECT_ROOT, "plants_system", "smart_objects", "resources", "plants_config.json"))
app.plants = PlantFactory.create_plants_from_json(FILENAME)
app.client = Main(FILENAME)

POLICY_PATH = os.path.abspath(os.path.join(PROJECT_ROOT, "plants_system", "smart_objects", "resources", "policies_conf.json"))
policy_manager = PolicyManager(POLICY_PATH)

@app.route('/')
def index():
    return "PlantPot API is running!", 200

@app.route('/api/plants/<plant_id>/telemetry', methods=['GET'])
def get_plant_telemetry(plant_id):
    # use app.plants which tests may initialize when importing this module
    plant : PlantDescriptor = next((p for p in app.plants if p.plant_id == plant_id), None)
    if not plant:
        return {"error": "Plant not found"}, 404
    telemetry_data = {}
    for device in plant.devices:
        for sensor in device.sensors:
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
    """Get list of all plants with basic info"""
    plants_data = []
    for plant in app.plants:
        # Get telemetry data for each plant
        telemetry_data = {}
        for device in plant.devices:
            for sensor in device.sensors:
                telemetry_data[sensor.device] = {
                    "type": sensor.type,
                    "value": sensor.value,
                    "unit": sensor.unit
                }
        
        # Map telemetry to frontend format
        plant_info = {
            "id": plant.plant_id,
            "name": getattr(plant, 'species', plant.plant_id),  # <-- correzione qui
            "type": getattr(plant, 'plant_type', 'Unknown'),
            "status": determine_plant_status(telemetry_data),
            "waterLevel": get_sensor_value(telemetry_data, 'tank_level', 50),
            "soilMoisture": get_sensor_value(telemetry_data, 'soil_moisture', 50),
            "temperature": get_sensor_value(telemetry_data, 'temperature', 20),
            "humidity": get_sensor_value(telemetry_data, 'humidity', 50),
            "lightLevel": get_sensor_value(telemetry_data, 'light', 50),
            "batteryLevel": get_sensor_value(telemetry_data, 'battery', 80),
            "waterFlow": get_sensor_value(telemetry_data, 'water_flow', 0),
            "isWatering": check_watering_status(plant),
            "lastWatered": "N/A"  # This would need to be tracked separately
        }
        plants_data.append(plant_info)
    
    return jsonify(plants_data), 200

@app.route('/api/alerts', methods=['GET'])
def get_alerts():
    """Get current alerts using PolicyManager"""
    
    try:
        alerts = []
        alert_id = 1
        
        for plant in app.plants:
            # Evaluate policies for each plant
            policy_manager.evaluate(plant)
            plant_alerts = policy_manager.alerts.get(plant.plant_id, [])
            
            for alert_msg in plant_alerts:
                # Determine alert type based on message content
                alert_type = "critical" if any(word in alert_msg.lower() for word in ["critical", "empty", "low"]) else "warning"
                
                alerts.append({
                    "id": alert_id,
                    "type": alert_type,
                    "plantName": getattr(plant, 'plant_name', plant.plant_id),
                    "message": alert_msg,
                    "timestamp": "Ora"
                })
                alert_id += 1
        
        return jsonify(alerts), 200
    
    except Exception as e:
        logging.error(f"Error getting alerts: {e}")
        # Fallback to original implementation
        return get_alerts_fallback()

def get_alerts_fallback():
    """Fallback alerts implementation"""
    alerts = []
    alert_id = 1
    
    for plant in app.plants:
        telemetry_data = {}
        for device in plant.devices:
            for sensor in device.sensors:
                telemetry_data[sensor.device] = {
                    "type": sensor.type,
                    "value": sensor.value,
                    "unit": sensor.unit
                }
        
        # Check for low battery
        battery_level = get_sensor_value(telemetry_data, 'battery', 100)
        if battery_level < 20:
            alerts.append({
                "id": alert_id,
                "type": "critical" if battery_level < 15 else "warning",
                "plantName": getattr(plant, 'plant_name', plant.plant_id),
                "message": f"Batteria {'critica' if battery_level < 15 else 'scarica'} ({battery_level}%)",
                "timestamp": "Ora"
            })
            alert_id += 1
        
        # Check for low water level
        water_level = get_sensor_value(telemetry_data, 'tank_level', 100)
        if water_level < 30:
            alerts.append({
                "id": alert_id,
                "type": "critical" if water_level < 15 else "warning",
                "plantName": getattr(plant, 'plant_name', plant.plant_id),
                "message": f"{'Serbatoio vuoto' if water_level < 15 else 'Livello acqua basso'} ({water_level}%)",
                "timestamp": "Ora"
            })
            alert_id += 1
    
    return jsonify(alerts), 200

@app.route('/api/alerts/<int:alert_id>', methods=['DELETE'])
def delete_alert(alert_id):
    """Delete/dismiss an alert"""
    # In a real implementation, you'd track alerts in a database
    return jsonify({"message": "Alert dismissed", "alert_id": alert_id}), 200

def get_sensor_value(telemetry_data, sensor_name, default_value):
    """Helper function to get sensor value or return default"""
    for device, data in telemetry_data.items():
        if sensor_name.lower() in device.lower():
            return data.get('value', default_value)
    return default_value

def determine_plant_status(telemetry_data):
    """Determine plant status based on telemetry data"""
    battery = get_sensor_value(telemetry_data, 'battery', 100)
    water_level = get_sensor_value(telemetry_data, 'tank_level', 100)
    
    if battery < 15 or water_level < 15:
        return "critical"
    elif battery < 30 or water_level < 30:
        return "warning"
    elif battery > 80 and water_level > 60:
        return "healthy"
    else:
        return "good"

def check_watering_status(plant):
    """Check if plant is currently watering"""
    for actuator in plant.actuators:
        if 'water' in actuator.device.lower():
            return actuator.status == 'on'
    return False

if __name__ == "__main__":
    # Avvia il server Flask
    app.run(host="127.0.0.1", port=5000)
