import json
from plants_system.smart_objects.sensors.humidity_sensor import HumiditySensor
from plants_system.smart_objects.actuators.irrigation_actuator import IrrigationActuator


class PlantDescriptor:
    def __init__(self, species, plant_id, devices=None):
        self.plant_id = plant_id
        self.species = species
        self.sensors=[ HumiditySensor(plant_id, 0, "%", 0, 100, "environment_telemetry", True)]
        self.actuators=[IrrigationActuator(plant_id, "water_metering", True)]


    def to_json(self):
        # Estrai tutti i sensori da tutti i dispositivi
        all_sensors = []
        all_actuators = []
        
        all_sensors.extend([sensor.type for sensor in self.sensors])
        all_actuators.extend([actuator.type for actuator in self.actuators])
        
        return json.dumps({
            "plant_id": self.plant_id,
            "species": self.species,
            "sensors": all_sensors,
            "actuators": all_actuators
        })