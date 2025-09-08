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
        """
        Converte il dispositivo in formato JSON.
        
        Returns:
            Stringa JSON contenente le informazioni del dispositivo
        """
        return json.dumps({
            "plant_id": self.plant_id,
            "device": self.device,
            "sensors": [sensor.type for sensor in self.sensors],
            "actuators": [actuator.type for actuator in self.actuators],
            "timestamp": getattr(self, 'timestamp', 0)
        })