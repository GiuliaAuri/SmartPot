from flask import Blueprint, jsonify
from datetime import datetime
from managers.config_manager import ConfigManager
from managers.plant_data_manager import PlantDataManager

system_bp = Blueprint('system', __name__)


@system_bp.route('/api/refresh', methods=['POST'])
def refresh_data():
    """Refresh plants data from JSON files"""
    from app import app
    
    data_manager = PlantDataManager()
    app.plants_data = data_manager.load_plants_data()
    return jsonify({"message": "Data refreshed successfully"}), 200


@system_bp.route('/api/status', methods=['GET'])
def get_status():
    """Get application status and data loading info"""
    from app import app, policy_evaluator
    
    config_manager = ConfigManager()
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


@system_bp.route('/api/config', methods=['GET'])
def get_config():
    """Get application configuration including update frequency"""
    config_manager = ConfigManager()
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
