from flask import Flask, jsonify, request
import logging
import json
import os
import sys
from datetime import datetime, timedelta
from flask_cors import CORS

# Add the project root to Python path to import factory_plants
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

app = Flask(__name__)
CORS(app, origins=["http://localhost:3000", "http://127.0.0.1:3000"], methods=["GET", "POST", "PUT", "DELETE", "OPTIONS"])

logging.basicConfig(level=logging.INFO)

@app.before_request
def handle_preflight():
    if request.method == "OPTIONS":
        response = jsonify({})
        response.headers.add("Access-Control-Allow-Origin", request.headers.get('Origin', '*'))
        response.headers.add('Access-Control-Allow-Headers', "Content-Type,Authorization")
        response.headers.add('Access-Control-Allow-Methods', "GET,PUT,POST,DELETE,OPTIONS")
        return response

class PlantDataManager:
    """Manages plant data loading and processing"""
    
    def __init__(self):
        self.project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
        self.plants_config = None
        self.policies_config = None
        self.plants_data = {}
        
    def load_configurations(self):
        """Load all configuration files"""
        try:
            # Load plants configuration
            plants_config_path = os.path.join(self.project_root, 'cloud_simulator', 'plants.json')
            with open(plants_config_path, 'r', encoding='utf-8') as f:
                self.plants_config = json.load(f)
            
            # Load policies configuration
            policies_config_path = os.path.join(self.project_root, 'plants_system', 'smart_objects', 'resources', 'policies_conf.json')
            with open(policies_config_path, 'r', encoding='utf-8') as f:
                self.policies_config = json.load(f)
            
            logging.info("Configuration files loaded successfully")
            return True
        except Exception as e:
            logging.error(f"Error loading configurations: {e}")
            return False
    
    def load_plants_data(self):
        """Load all plants data from log files"""
        if not self.plants_config:
            return {}
        
        plants_data = {}
        for plant_config in self.plants_config:
            plant_id = plant_config['plant_id']
            
            # Load plant-specific data
            log_file = os.path.join(self.project_root, 'cloud_simulator', 'plants_log', f'{plant_id}.json')
            if os.path.exists(log_file):
                try:
                    with open(log_file, 'r', encoding='utf-8') as f:
                        plant_log_data = json.load(f)
                    
                    # Extract the first (and only) plant data from the array
                    if isinstance(plant_log_data, list) and len(plant_log_data) > 0:
                        plant_log = plant_log_data[0]
                    else:
                        plant_log = plant_log_data
                    
                    # Merge config and log data
                    plants_data[plant_id] = {
                        **plant_config,
                        **plant_log
                    }
                except json.JSONDecodeError as e:
                    logging.warning(f"JSON decode error in {log_file}: {e}. Using config only.")
                    plants_data[plant_id] = plant_config
            else:
                logging.warning(f"Log file not found for plant {plant_id}")
                plants_data[plant_id] = plant_config
        
        self.plants_data = plants_data
        logging.info(f"Successfully loaded data for {len(plants_data)} plants")
        return plants_data

class SensorDataProcessor:
    """Processes sensor data and extracts values"""
    
    @staticmethod
    def extract_sensor_value(sensors, sensor_name, default_value=0.0):
        """Extract sensor value from sensors array"""
        if isinstance(sensors, list):
            for sensor in sensors:
                if sensor.get('sensor') == sensor_name:
                    values = sensor.get('values', [])
                    if values:
                        raw_value = values[-1].get('value', default_value)
                        return raw_value
        return default_value
    
    @staticmethod
    def get_sensor_device(sensors, sensor_name):
        """Get the device name for a specific sensor"""
        if isinstance(sensors, list):
            for sensor in sensors:
                if sensor.get('sensor') == sensor_name:
                    return sensor.get('device', 'unknown')
        return 'unknown'
    
    @staticmethod
    def get_all_sensors_by_device(sensors):
        """Group sensors by device"""
        devices = {}
        if isinstance(sensors, list):
            for sensor in sensors:
                device = sensor.get('device', 'unknown')
                if device not in devices:
                    devices[device] = []
                devices[device].append(sensor)
        return devices

class ActuatorDataProcessor:
    """Processes actuator data and extracts values"""
    
    @staticmethod
    def get_actuator_value(actuators, actuator_name, default_value=False):
        """Get the last value of an actuator"""
        if isinstance(actuators, list):
            for actuator in actuators:
                if actuator.get('actuator') == actuator_name:
                    values = actuator.get('values', [])
                    if values:
                        return values[-1].get('value', default_value)
        return default_value
    
    @staticmethod
    def get_last_activation_time(actuators, actuator_name):
        """Get the timestamp of the last activation of an actuator"""
        if isinstance(actuators, list):
            for actuator in actuators:
                if actuator.get('actuator') == actuator_name:
                    values = actuator.get('values', [])
                    if values:
                        return values[-1].get('timestamp', None)
        return None
    
    @staticmethod
    def calculate_time_since_last_watering(actuators):
        """Calculate time since last irrigation activation"""
        if isinstance(actuators, list):
            for actuator in actuators:
                if actuator.get('actuator') == 'irrigation':
                    values = actuator.get('values', [])
                    if not values:
                        return None
                    
                    # Get the most recent irrigation state
                    last_value = values[-1]
                    last_timestamp = last_value.get('timestamp')
                    last_state = last_value.get('value')
                    
                    # If irrigation is currently active, return 0 time difference
                    if last_state == True:
                        return datetime.now() - datetime.now()  # Returns timedelta(0)
                    
                    # If irrigation is not active, find the last time it was active
                    irrigation_times = []
                    for value_data in values:
                        if value_data.get('value') == True:  # When irrigation was active
                            irrigation_times.append(value_data.get('timestamp'))
                    
                    if irrigation_times:
                        # Get the most recent irrigation time
                        last_irrigation = max(irrigation_times)
                        try:
                            # Convert timestamp to datetime
                            irrigation_time = datetime.fromtimestamp(int(last_irrigation))
                            time_diff = datetime.now() - irrigation_time
                            return time_diff
                        except (ValueError, TypeError):
                            return None
        return None

class PolicyEvaluator:
    """Evaluates policies based on sensor data"""
    
    def __init__(self, policies_config):
        self.policies_config = policies_config
    
    def get_plant_policies(self, plant_id):
        """Get policies for a specific plant"""
        if isinstance(self.policies_config, list):
            for plant_policy in self.policies_config:
                if plant_policy.get('plant_id') == plant_id:
                    return plant_policy.get('policies', [])
        return []
    
    def evaluate_policies(self, plant_id, sensors):
        """Evaluate all policies for a plant and return alerts"""
        policies = self.get_plant_policies(plant_id)
        alerts = []
        
        for policy in policies:
            sensor_name = policy.get('sensor')
            condition = policy.get('condition')
            threshold_value = policy.get('value')
            action = policy.get('action')
            
            if sensor_name and condition and threshold_value is not None:
                current_value = SensorDataProcessor.extract_sensor_value(sensors, sensor_name)
                
                # Evaluate condition
                condition_met = False
                if condition == '<':
                    condition_met = current_value < threshold_value
                elif condition == '>':
                    condition_met = current_value > threshold_value
                elif condition == '==':
                    condition_met = current_value == threshold_value
                elif condition == '<=':
                    condition_met = current_value <= threshold_value
                elif condition == '>=':
                    condition_met = current_value >= threshold_value
                
                if condition_met:
                    if action == 'alert':
                        alerts.append({
                            'type': 'warning',
                            'message': policy.get('message', f'{sensor_name} condition met'),
                            'sensor': sensor_name,
                            'value': current_value,
                            'threshold': threshold_value
                        })
                    elif action == 'activate':
                        alerts.append({
                            'type': 'info',
                            'message': f'{policy.get("actuator", "actuator")} should be activated',
                            'sensor': sensor_name,
                            'value': current_value,
                            'threshold': threshold_value
                        })
        
        return alerts

class PlantStatusEvaluator:
    """Evaluates overall plant status based on policies and sensor data"""
    
    def __init__(self, policy_evaluator):
        self.policy_evaluator = policy_evaluator
    
    def determine_plant_status(self, plant_id, sensors):
        """Determine plant status based on number of alerts"""
        alerts = self.policy_evaluator.evaluate_policies(plant_id, sensors)
        
        # Count total alerts (excluding irrigation-related alerts)
        irrigation_keywords = ['irrigation', 'irrigazione', 'should be activated', 'should be deactivated']
        non_irrigation_alerts = []
        
        for alert in alerts:
            message = alert.get('message', '').lower()
            if not any(keyword in message for keyword in irrigation_keywords):
                non_irrigation_alerts.append(alert)
        
        alert_count = len(non_irrigation_alerts)
        
        # Determine status based on alert count
        if alert_count == 0:
            return "good"        # 0 alert -> good
        elif alert_count == 1:
            return "healthy"     # 1 alert -> healthy  
        elif alert_count == 2:
            return "warning"     # 2 alerts -> warning
        else:
            return "critical"    # more than 2 alerts -> critical

class ConfigManager:
    """Manages application configuration"""
    
    def __init__(self):
        self.config = self.load_config()
    
    def load_config(self):
        """Load configuration from config.json"""
        try:
            config_path = os.path.join(os.path.dirname(__file__), 'config.json')
            with open(config_path, 'r', encoding='utf-8') as f:
                return json.load(f)
        except Exception as e:
            logging.warning(f"Could not load config.json: {e}. Using defaults.")
            return {
                "server": {"host": "127.0.0.1", "port": 5000, "debug": True},
                "update": {"frequency_seconds": 30},
                "data": {"precision": 1}
            }
    
    def get_server_config(self):
        """Get server configuration"""
        return self.config.get("server", {"host": "127.0.0.1", "port": 5000, "debug": True})
    
    def get_update_frequency(self):
        """Get update frequency in seconds"""
        return self.config.get("update", {}).get("frequency_seconds", 30)
    
    def get_data_precision(self):
        """Get data precision (decimal places)"""
        return self.config.get("data", {}).get("precision", 1)

# Initialize managers
config_manager = ConfigManager()
data_manager = PlantDataManager()
sensor_processor = SensorDataProcessor()
actuator_processor = ActuatorDataProcessor()

# Load configurations and data
if data_manager.load_configurations():
    app.plants_data = data_manager.load_plants_data()
    policy_evaluator = PolicyEvaluator(data_manager.policies_config)
    status_evaluator = PlantStatusEvaluator(policy_evaluator)
else:
    app.plants_data = {}
    policy_evaluator = None
    status_evaluator = None

@app.route('/api/plants/<plant_id>/telemetry', methods=['GET'])
def get_plant_telemetry(plant_id):
    """Get telemetry data for a specific plant"""
    if plant_id not in app.plants_data:
        return {"error": "Plant not found"}, 404
    
    plant_data = app.plants_data[plant_id]
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

@app.route('/api/plants/<plant_id>/actuators/<actuator_name>/command', methods=['POST'])
def post_actuator_command(plant_id, actuator_name):
    """Send command to plant actuator"""
    if plant_id not in app.plants_data:
        return {"error": "Plant not found"}, 404

    plant_data = app.plants_data[plant_id]
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
    
    # In a real implementation, this would also send to MQTT
    # TODO: invocare la funzione inviare command all'attuatore via MQTT
    
    return {
        "status": "success",
        "plant_id": plant_id,
        "actuator": actuator_name,
        "command": command,
        "timestamp": datetime.now().isoformat()
    }, 200

@app.route('/api/plants', methods=['GET'])
def get_all_plants():
    """Get list of all plants with current data"""
    plants_list = []
    
    for plant_id, plant_data in app.plants_data.items():
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
        if status_evaluator:
            status = status_evaluator.determine_plant_status(plant_id, sensors)
        
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

@app.route('/api/alerts', methods=['GET'])
def get_alerts():
    """Get current alerts from all plants based on policies"""
    all_alerts = []
    alert_id = 1
    
    for plant_id, plant_data in app.plants_data.items():
        sensors = plant_data.get('sensors', [])
        
        # Get alerts from plant log file (if any)
        plant_alerts = plant_data.get('alerts', [])
        for alert in plant_alerts:
            all_alerts.append({
                "id": alert_id,
                "type": alert.get('type', 'info'),
                "plantName": plant_id,  # Usa sempre l'ID per consistenza
                "message": alert.get('message', ''),
                "timestamp": format_timestamp(alert.get('timestamp', ''))
            })
            alert_id += 1
        
        # Generate alerts based on policies
        if policy_evaluator:
            policy_alerts = policy_evaluator.evaluate_policies(plant_id, sensors)
            for alert in policy_alerts:
                all_alerts.append({
                    "id": alert_id,
                    "type": alert.get('type', 'warning'),
                    "plantName": plant_id,  # Usa sempre l'ID per consistenza
                    "message": alert.get('message', ''),
                    "timestamp": "Ora",
                    "sensor": alert.get('sensor', ''),
                    "value": alert.get('value', 0),
                    "threshold": alert.get('threshold', 0)
                })
                alert_id += 1
    
    return jsonify(all_alerts), 200

@app.route('/api/alerts/<int:alert_id>', methods=['DELETE'])
def delete_alert(alert_id):
    """Delete/dismiss an alert"""
    return jsonify({"message": "Alert dismissed", "alert_id": alert_id}), 200

@app.route('/api/refresh', methods=['POST'])
def refresh_data():
    """Refresh plants data from JSON files"""
    app.plants_data = data_manager.load_plants_data()
    return jsonify({"message": "Data refreshed successfully"}), 200

@app.route('/api/status', methods=['GET'])
def get_status():
    """Get application status and data loading info"""
    plants_count = len(app.plants_data)
    update_freq = config_manager.get_update_frequency()
    return jsonify({
        "status": "running",
        "plants_loaded": plants_count,
        "data_source": "cloud_simulator JSON files",
        "policies_loaded": policy_evaluator is not None,
        "update_frequency": f"{update_freq} seconds",
        "last_update": datetime.now().isoformat()
    }), 200

@app.route('/api/config', methods=['GET'])
def get_config():
    """Get application configuration including update frequency"""
    update_freq = config_manager.get_update_frequency()
    precision = config_manager.get_data_precision()
    return jsonify({
        "update_frequency_seconds": update_freq,
        "update_frequency_description": f"The dashboard automatically refreshes plant data every {update_freq} seconds",
        "data_precision": f"All numeric values are rounded to {precision} decimal place{'s' if precision != 1 else ''}",
        "supported_devices": [
            "environment_telemetry",
            "tank_monitoring", 
            "water_metering"
        ],
        "supported_sensors": [
            "temperature",
            "humidity", 
            "lightness",
            "battery_level",
            "level_tank",
            "water_flow",
        ],
        "supported_actuators": [
            "irrigation"
        ]
    }), 200

def format_timestamp(timestamp_str):
    """Format timestamp for display"""
    if not timestamp_str:
        return "N/A"
    
    try:
        # Try to parse as Unix timestamp first
        if timestamp_str.isdigit():
            dt = datetime.fromtimestamp(int(timestamp_str))
            return dt.strftime("%H:%M")
        
        # Try to parse ISO format timestamp
        dt = datetime.fromisoformat(timestamp_str.replace('Z', '+00:00'))
        return dt.strftime("%H:%M")
    except:
        return timestamp_str

if __name__ == "__main__":
    server_config = config_manager.get_server_config()
    app.run(
        host=server_config.get("host", "127.0.0.1"),
        port=server_config.get("port", 5000),
        debug=server_config.get("debug", True)
    )