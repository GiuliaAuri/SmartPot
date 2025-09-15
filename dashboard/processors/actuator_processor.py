from datetime import datetime


class ActuatorDataProcessor:
    """Processes actuator data and extracts values"""
    
    @staticmethod
    def get_actuator_value(actuators, actuator_name, default_value=False):
        """Get the last value of an actuator"""
        if isinstance(actuators, list):
            for actuator in actuators:
                # Gestisce sia dizionari che stringhe
                if isinstance(actuator, dict):
                    if actuator.get('type') == actuator_name:
                        values = actuator.get('values', [])
                        if values:
                            return values[-1].get('value', default_value)
                elif isinstance(actuator, str):
                    # Se è una stringa, controlla se corrisponde al nome dell'attuatore
                    if actuator == actuator_name:
                        return default_value  # Per stringhe, restituisce il valore di default
        return default_value
    
    @staticmethod
    def get_last_activation_time(actuators, actuator_name):
        """Get the timestamp of the last activation of an actuator"""
        if isinstance(actuators, list):
            for actuator in actuators:
                # Gestisce sia dizionari che stringhe
                if isinstance(actuator, dict):
                    if actuator.get('type') == actuator_name:
                        values = actuator.get('values', [])
                        if values:
                            return values[-1].get('timestamp', None)
                elif isinstance(actuator, str):
                    # Se è una stringa, non può avere timestamp
                    if actuator == actuator_name:
                        return None
        return None
    
    @staticmethod
    def calculate_time_since_last_watering(actuators):
        """Calculate time since last irrigation activation"""
        if isinstance(actuators, list):
            for actuator in actuators:
                # Gestisce sia dizionari che stringhe
                if isinstance(actuator, dict):
                    if actuator.get('type') == 'irrigation':
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
                elif isinstance(actuator, str):
                    # Se è una stringa, non può avere dati storici
                    if actuator == 'irrigation':
                        return None
        return None
