import json
import uuid

from model import Sensor, SwitchActuator, SwitchActuator


class PlantDescriptor:
    def __init__(self, species, sensors:Sensor=None, actuators: SwitchActuator=None):
        self.plant_id = "plant_"+ str(uuid.uuid4())
        self.species = species
        self.sensors = sensors if sensors is not None else []
        self.actuators = actuators if actuators is not None else []

    def to_json(self):
        
        return json.dumps({
            "plant_id": self.plant_id,
            "species": self.species,
            "sensors": [sensor.type for sensor in self.sensors],
            "actuators": [actuator.type for actuator in self.actuators]
        })