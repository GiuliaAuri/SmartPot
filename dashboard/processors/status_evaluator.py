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
