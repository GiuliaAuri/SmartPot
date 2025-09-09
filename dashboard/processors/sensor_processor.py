class SensorDataProcessor:
    """Processes sensor data and extracts values"""
    
    @staticmethod
    def extract_sensor_value(sensors, sensor_name, default_value=0.0):
        """
        Extract sensor value from sensors array.
        
        Handles both list of dictionaries (from JSON files) and list of strings (from plant descriptor).
        
        Args:
            sensors: List of sensor data (dicts or strings)
            sensor_name: Name of the sensor to extract
            default_value: Default value if sensor not found
            
        Returns:
            float: Sensor value or default value
        """
        if isinstance(sensors, list):
            for sensor in sensors:
                # Handle dictionary format (from JSON files)
                if isinstance(sensor, dict):
                    if sensor.get('sensor') == sensor_name:
                        values = sensor.get('values', [])
                        if values:
                            raw_value = values[-1].get('value', default_value)
                            return raw_value
                # Handle string format (from plant descriptor)
                elif isinstance(sensor, str):
                    if sensor == sensor_name:
                        # For string sensors, we need to get the value from the plant descriptor
                        # This is a fallback - in practice, we should have the actual value
                        return default_value
        return default_value
    
    @staticmethod
    def get_sensor_device(sensors, sensor_name):
        """
        Get the device name for a specific sensor.
        
        Handles both list of dictionaries (from JSON files) and list of strings (from plant descriptor).
        
        Args:
            sensors: List of sensor data (dicts or strings)
            sensor_name: Name of the sensor to find
            
        Returns:
            str: Device name or 'unknown'
        """
        if isinstance(sensors, list):
            for sensor in sensors:
                # Handle dictionary format (from JSON files)
                if isinstance(sensor, dict):
                    if sensor.get('sensor') == sensor_name:
                        return sensor.get('device', 'unknown')
                # Handle string format (from plant descriptor)
                elif isinstance(sensor, str):
                    if sensor == sensor_name:
                        return 'unknown'  # String sensors don't have device info
        return 'unknown'
    
    @staticmethod
    def get_all_sensors_by_device(sensors):
        """
        Group sensors by device.
        
        Handles both list of dictionaries (from JSON files) and list of strings (from plant descriptor).
        
        Args:
            sensors: List of sensor data (dicts or strings)
            
        Returns:
            dict: Dictionary with device names as keys and lists of sensors as values
        """
        devices = {}
        if isinstance(sensors, list):
            for sensor in sensors:
                # Handle dictionary format (from JSON files)
                if isinstance(sensor, dict):
                    device = sensor.get('device', 'unknown')
                    if device not in devices:
                        devices[device] = []
                    devices[device].append(sensor)
                # Handle string format (from plant descriptor)
                elif isinstance(sensor, str):
                    device = 'unknown'  # String sensors don't have device info
                    if device not in devices:
                        devices[device] = []
                    devices[device].append(sensor)
        return devices
