import logging
import random
import time
from model.Sensor import Sensor

class WaterFlowSensor(Sensor[float]):
    def __init__(self, initial_value: float, unit: str, min_value: float, max_value: float, device:str):
        super().__init__(initial_value, unit, min_value, max_value, "water_flow", device)

    def update(self):
        self.value = random.uniform(self.min_value, self.max_value)
        self.timestamp = int(time.time())
        logging.info(f"Updated water flow measurement: {self.value} {self.unit} at {self.timestamp}")
