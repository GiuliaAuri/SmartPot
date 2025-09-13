import logging
from plants_system.smart_objects.models.Device import Device
from plants_system.smart_objects.sensors.battery_level_sensor import BatteryLevelSensor
from plants_system.smart_objects.sensors.humidity_sensor import HumiditySensor
from plants_system.smart_objects.sensors.lightness_sensor import LightnessSensor
from plants_system.smart_objects.sensors.temperature_sensor import TemperatureSensor

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("environment_telemetry")

class EnvironmentTelemetryData(Device):
    def __init__(self, plant_id):
        self.plant_id = plant_id  
        self.device = "environment_telemetry"
        sensors = [
            BatteryLevelSensor(plant_id, initial_value=100.0, unit="%", min_value=0.0, max_value=5.0, device=self.device, is_real=False),
            TemperatureSensor(self.plant_id, initial_value=0.0, unit="°C", min_value=0.0, max_value=50.0, device=self.device, is_real=False),
            HumiditySensor(self.plant_id, initial_value=00.0, unit="%", min_value=0.0, max_value=100.0, device=self.device, is_real=False),
            LightnessSensor(self.plant_id, initial_value=200.0, unit="lx", min_value=200.0, max_value=60000.0, device=self.device, is_real=False)
        ]
        super().__init__(plant_id, self.device, sensors=sensors)

