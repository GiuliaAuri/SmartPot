import json
from smart_objects.sensors.humidity_sensor import HumiditySensor
from smart_objects.actuators.irrigation_actuator import IrrigationActuator


class PlantDescriptor:
    def __init__(self, species, plant_id, devices=None, sensor_config=None):
        self.plant_id = plant_id
        self.species = species
        
        if sensor_config:
            self.sensors = [HumiditySensor(
                plant_id, 
                sensor_config.get("initial_value", 80.0),
                sensor_config.get("unit", "%"),
                sensor_config.get("min_value", 50.0),
                sensor_config.get("max_value", 160.0),
                "environment_telemetry", 
                sensor_config.get("is_real", True)
            )]
        else:
           
            self.sensors = [HumiditySensor(plant_id, 80.0, "%", 50.0, 160.0, "environment_telemetry", True)]
        
        self.actuators = [IrrigationActuator(plant_id, "water_metering")]


    def to_json(self):
       
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