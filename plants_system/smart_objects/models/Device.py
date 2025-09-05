from abc import ABC
import json
import time
import logging

from plants_system.smart_objects.models.Sensor import Sensor
from plants_system.smart_objects.models.SwitchActuator import SwitchActuator



class Device(ABC):

    def __init__(self, plant_id: str, device: str, sensors: list[Sensor] = None, actuators: list[SwitchActuator] = None):
        self.plant_id = plant_id
        self.device = device
        self.sensors = sensors if sensors is not None else []
        self.actuators = actuators if actuators is not None else []


    def update_measurements(self):
        for sensor in self.sensors:
            sensor.update()

        self.timestamp = int(time.time())
        logging.info(f"Updated: {self.to_json()}")

    def to_json(self):
        return json.dumps(self, default=lambda o: o.__dict__)