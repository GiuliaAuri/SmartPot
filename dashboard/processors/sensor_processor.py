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
