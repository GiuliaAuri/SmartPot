import logging
import random
import time
from plants_system.smart_objects.models.Sensor import Sensor

class LevelTankSensor(Sensor):
    def __init__(self, plant_id: str, initial_value: float, unit: str, min_value: float, max_value: float, device:str):
        super().__init__(plant_id, initial_value, unit, min_value, max_value, "level_tank", device)

    def update(self):
        self.value = random.uniform(self.min_value, self.max_value)
        self.timestamp = int(time.time())
        logging.info(f"Updated level tank measurement: {self.value} {self.unit} at {self.timestamp} - plant: {self.plant_id}")