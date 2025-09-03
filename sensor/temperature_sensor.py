import logging
from random import random
from model.Sensor import Sensor

class TemperatureSensor(Sensor[float]):
    def __init__(self, initial_value: float, unit: str, min_value: float, max_value: float):
        super().__init__(initial_value, unit, min_value, max_value, "temperature")

    def update(self):
        self.value = random.uniform(self.min_value, self.max_value)
        logging.info(f"Updated temperature measurement: {self.value} {self.unit}")
