import json

from model import Sensor, SwitchActuator, SwitchActuator


class PlantDescriptor:
    def __init__(self, plant_id, species, sensors:Sensor=None, actuators: SwitchActuator=None):
        self.plant_id = plant_id
        #TODO self.plant_id="plant_"+uuid.uuid
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