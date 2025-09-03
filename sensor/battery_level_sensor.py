import logging
from random import random
from model.Sensor import Sensor

class BatteryLevelSensor(Sensor[float]):
    def __init__(self, initial_value: float, unit: str, min_value: float, max_value: float):
        super().__init__(initial_value, unit, min_value, max_value, "battery_level")

    def update(self):
        self.value = max(0, self.value - random.uniform(self.min_value, self.max_value))
        logging.info(f"Updated battery level measurement: {self.value} {self.unit}")
