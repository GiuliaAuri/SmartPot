from flask import Blueprint, jsonify, current_app
from processors.policy_evaluator import PolicyEvaluator
from utils.helpers import format_timestamp
alerts_bp = Blueprint('alerts', __name__)


@alerts_bp.route('/api/alerts', methods=['GET'])
def get_alerts():
    """Get current alerts from all plants based on policies"""
    
    all_alerts = []
    alert_id = 1
    
    for plant_id, plant_data in current_app.plants_data.items():
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
        if current_app.policy_evaluator:
            policy_alerts = current_app.policy_evaluator.evaluate_policies(plant_id, sensors)
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


@alerts_bp.route('/api/alerts/<int:alert_id>', methods=['DELETE'])
def delete_alert(alert_id):
    """Delete/dismiss an alert"""
    return jsonify({"message": "Alert dismissed", "alert_id": alert_id}), 200
