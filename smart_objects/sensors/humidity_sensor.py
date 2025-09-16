import logging
import random
import time
from smart_objects.models.Sensor import Sensor

class HumiditySensor(Sensor[float]):
    def __init__(self, plant_id: str, initial_value: float, unit: str, min_value: float, max_value: float, device: str, is_real: bool = False):
        super().__init__(plant_id, initial_value, unit, min_value, max_value, "humidity", device)

        
