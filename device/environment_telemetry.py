import json
import time
import logging

from sensors.battery_level_sensor import BatteryLevelSensor
from sensors.humidity_sensor import HumiditySensor
from sensors.lightness_sensor import LightnessSensor
from sensors.temperature_sensor import TemperatureSensor

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("environment_telemetry")

class EnvironmentTelemetryData:

    def __init__(self, plant_id: str):
        self.plant_id = plant_id
        self.device = "environment_telemetry"
        self.batteryLevel = BatteryLevelSensor(initial_value=100.0, unit="%", min_value=0.0, max_value=5.0, device=self.device) #max_increse e max_decrease
        self.temperature = TemperatureSensor(initial_value=0.0, unit="°C", min_value=0.0, max_value=50.0, device=self.device)
        self.humidity = HumiditySensor(initial_value=0.0, unit="%", min_value=0.0, max_value=100.0, device=self.device)
        self.lightness = LightnessSensor(initial_value=0.0, unit="lx", min_value=200.0, max_value=60000.0, device=self.device)
        self.timestamp = int(time.time())

    def update_measurements(self):
        self.temperature.update()
        self.humidity.update()
        self.lightness.update()
        self.batteryLevel.update()
        self.timestamp = int(time.time())
        logger.info(f"Updated: {self.to_json()}")

    def to_json(self):
        return json.dumps(self, default=lambda o: o.__dict__)
