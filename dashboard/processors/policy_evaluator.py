from processors.sensor_processor import SensorDataProcessor


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
