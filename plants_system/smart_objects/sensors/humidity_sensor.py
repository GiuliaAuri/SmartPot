import logging
import random
import time
from plants_system.smart_objects.models.Sensor import Sensor

class HumiditySensor(Sensor[float]):
    def __init__(self, plant_id: str, initial_value: float, unit: str, min_value: float, max_value: float, device: str, is_real: bool = False):
        super().__init__(plant_id, initial_value, unit, min_value, max_value, "humidity", device, is_real)

    def update(self):
        self.value = round(random.uniform(self.min_value, self.max_value),1)
        self.timestamp = int(time.time())
        logging.info(f"Updated humidity measurement: {self.value} {self.unit} at {self.timestamp} - plant: {self.plant_id}")
