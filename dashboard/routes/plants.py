from flask import Blueprint, jsonify, request, current_app
from datetime import datetime
import logging
from processors.sensor_processor import SensorDataProcessor
from processors.actuator_processor import ActuatorDataProcessor
from processors.status_evaluator import PlantStatusEvaluator
from utils.helpers import format_timestamp
plants_bp = Blueprint('plants', __name__)


@plants_bp.route('/api/plants/<plant_id>/telemetry', methods=['GET'])
def get_plant_telemetry(plant_id):
    """Get telemetry data for a specific plant"""

    
    if plant_id not in current_app.plants_data:
        return {"error": "Plant not found"}, 404
    
    plant_data = current_app.plants_data[plant_id]
    sensors = plant_data.get('sensors', [])
    
    # Group sensors by device
    devices = SensorDataProcessor.get_all_sensors_by_device(sensors)
    
    telemetry_data = {
        "plant_id": plant_id,
        "timestamp": plant_data.get('timestamp', datetime.now().isoformat()),
        "devices": {}
    }
    
    for device_name, device_sensors in devices.items():
        telemetry_data["devices"][device_name] = {
            "device": device_name,
            "sensors": []
        }
        
        for sensor in device_sensors:
            sensor_name = sensor.get('sensor')
            values = sensor.get('values', [])
            latest_value = values[-1] if values else {}
            
            telemetry_data["devices"][device_name]["sensors"].append({
                "name": sensor_name,
                "value": latest_value.get('value', 0),
                "timestamp": latest_value.get('timestamp', ''),
                "unit": sensor.get('unit', '')
            })
    
    return jsonify(telemetry_data), 200


@plants_bp.route('/api/plants/<plant_id>/actuators/<actuator_name>/command', methods=['POST'])
def post_actuator_command(plant_id, actuator_name):
    """Send command to plant actuator"""
    
    if plant_id not in current_app.plants_data:
        return {"error": "Plant not found"}, 404

    plant_data = current_app.plants_data[plant_id]
    actuators = plant_data.get('actuators', [])
    
    command = request.json.get("command")
    if not command:
        return {"error": "No command provided"}, 400

    logging.info(f"Received command for {actuator_name} of plant {plant_id}: {command}")
    
    # Update actuator state in memory
    current_time = datetime.now().timestamp()
    
    # Find the actuator and update its state
    actuator_found = False
    for actuator in actuators:
        if actuator.get('actuator') == actuator_name:
            actuator_found = True
            if 'values' not in actuator:
                actuator['values'] = []
            
            # Determine the new value based on command
            new_value = False
            if command in ['on', 'start', 'true', '1']:
                new_value = True
            elif command in ['off', 'stop', 'false', '0']:
                new_value = False
            
            # Only add if value changed
            if not actuator['values'] or actuator['values'][-1]['value'] != new_value:
                actuator['values'].append({
                    "value": new_value,
                    "timestamp": str(int(current_time))
                })
                logging.info(f"Updated actuator {actuator_name} to {new_value}")
            break
    
    # If actuator not found, create it
    if not actuator_found:
        new_value = command in ['on', 'start', 'true', '1']
        actuators.append({
            "actuator": actuator_name,
            "device": f"{actuator_name}_device",
            "values": [{
                "value": new_value,
                "timestamp": str(int(current_time))
            }]
        })
        logging.info(f"Created new actuator {actuator_name} with value {new_value}")

    
    return {
        "status": "success",
        "plant_id": plant_id,
        "actuator": actuator_name,
        "command": command,
        "timestamp": datetime.now().isoformat()
    }, 200


@plants_bp.route('/api/plants', methods=['GET'])
def get_all_plants():
    """Get list of all plants with current data"""

    
    plants_list = []
    
    for plant_id, plant_data in current_app.plants_data.items():
        sensors = plant_data.get('sensors', [])
        actuators = plant_data.get('actuators', [])
        
        # Extract sensor values and convert to percentages
        temperature = SensorDataProcessor.extract_sensor_value(sensors, 'temperature', 20.0)
        humidity = SensorDataProcessor.extract_sensor_value(sensors, 'humidity', 50.0)
        light_level_raw = SensorDataProcessor.extract_sensor_value(sensors, 'lightness', 30000.0)  # Raw lux value
        battery_level = SensorDataProcessor.extract_sensor_value(sensors, 'battery_level', 80.0)
        tank_level_raw = SensorDataProcessor.extract_sensor_value(sensors, 'level_tank', 0.5)  # Raw liters value
        water_flow = SensorDataProcessor.extract_sensor_value(sensors, 'water_flow', 0.0)
        
        # Convert raw values to percentages
        # Tank level: 0-1 liters -> 0-100%
        tank_level = min(100, max(0, tank_level_raw * 100))
        
        # Light level: 200-60000 lux -> 0-100%
        light_level = min(100, max(0, ((light_level_raw - 200) / (60000 - 200)) * 100))
        
        # Get irrigation status
        is_watering = ActuatorDataProcessor.get_actuator_value(actuators, 'irrigation', False)
        time_since_watering = ActuatorDataProcessor.calculate_time_since_last_watering(actuators)
        
        # Format last watered time
        last_watered = "N/A"
        if time_since_watering is not None:
            # If irrigation is currently active, show "Ora"
            if is_watering and time_since_watering.total_seconds() == 0:
                last_watered = "Ora"
            elif time_since_watering.days > 0:
                last_watered = f"{time_since_watering.days} giorni fa"
            elif time_since_watering.seconds > 3600:
                hours = time_since_watering.seconds // 3600
                last_watered = f"{hours} ore fa"
            else:
                minutes = time_since_watering.seconds // 60
                last_watered = f"{minutes} minuti fa"
        
        # Determine overall status
        status = "unknown"
        if current_app.status_evaluator:
            status = current_app.status_evaluator.determine_plant_status(plant_id, sensors)
        
        plant_info = {
            "id": plant_id,
            "name": plant_id,  # Usa sempre l'ID come nome per consistenza
            "type": plant_data.get('species', 'Unknown'),  # Use species instead of plant_type
            "species": plant_data.get('species', ''),
            "status": status,
            "waterLevel": tank_level,
            "temperature": temperature,
            "humidity": humidity,
            "lightLevel": light_level,
            "batteryLevel": battery_level,
            "waterFlow": water_flow,
            "isWatering": is_watering,
            "lastWatered": last_watered
        }
        plants_list.append(plant_info)
    
    return jsonify(plants_list), 200
