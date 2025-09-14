import json
import os
import glob
import logging
import time
from flask import Blueprint, jsonify, current_app
from processors.policy_evaluator import PolicyEvaluator
from utils.helpers import format_timestamp
alerts_bp = Blueprint('alerts', __name__)


@alerts_bp.route('/api/alerts', methods=['GET'])
def get_alerts():
    """Get current alerts from all plants based on policies"""
    
    # Ricarica i dati dai file JSON ad ogni richiesta
    log_dir = r"C:\Users\giuli\Documents\unimore\internet of things\Plants-System\cloud_simulator\plants_log"
    
    logging.info(f"Loading alerts from: {log_dir}")
    
    # Carica direttamente i file JSON
    plants_data = {}
    
    for json_file in glob.glob(os.path.join(log_dir, '*.json')):
        try:
            logging.info(f"Loading file: {json_file}")
            with open(json_file, 'r', encoding='utf-8') as f:
                data = json.load(f)
                logging.info(f"Loaded data: {len(data) if data else 0} items")
                if data and isinstance(data, list) and len(data) > 0:
                    plant_id = data[0].get('plant_id')
                    logging.info(f"Found plant_id: {plant_id}")
                    if plant_id:
                        plants_data[plant_id] = data[0]
        except Exception as e:
            logging.error(f"Error loading {json_file}: {e}")
            continue
    
    logging.info(f"Total plants loaded for alerts: {len(plants_data)}")
    
    all_alerts = []
    alert_id = 1
    
    for plant_id, plant_data in plants_data.items():
        # Get alerts from plant log file (if any)
        plant_alerts = plant_data.get('alerts', [])
        logging.info(f"Found {len(plant_alerts)} saved alerts for plant {plant_id}")
        
        for alert in plant_alerts:
            all_alerts.append({
                "id": alert_id,
                "type": alert.get('type', 'info'),
                "plantName": plant_id,
                "message": alert.get('message', ''),
                "timestamp": format_timestamp(alert.get('timestamp', ''))
            })
            alert_id += 1
    
    logging.info(f"Total alerts found: {len(all_alerts)}")
    
    return jsonify(all_alerts), 200


@alerts_bp.route('/api/alerts/<int:alert_id>', methods=['DELETE'])
def delete_alert(alert_id):
    """Delete/dismiss an alert"""
    return jsonify({"message": "Alert dismissed", "alert_id": alert_id}), 200
