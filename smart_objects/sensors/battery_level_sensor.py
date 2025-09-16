import logging
import random
import time
from smart_objects.models.Sensor import Sensor

class BatteryLevelSensor(Sensor[float]):
    def __init__(self, plant_id: str, initial_value: float, unit: str, min_value: float, max_value: float, device: str, is_real: bool = False):
        super().__init__(plant_id, initial_value, unit, min_value, max_value, "battery_level", device)

    def update(self):
        self.value = round(max(0, self.value - random.uniform(self.min_value, self.max_value)),1)
        self.timestamp = int(time.time())
        logging.info(f"Updated battery level measurement: {self.value} {self.unit} at {self.timestamp} - plant: {self.plant_id}")
