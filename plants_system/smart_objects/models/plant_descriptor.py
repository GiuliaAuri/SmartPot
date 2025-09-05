import json
from plants_system.smart_objects.devices.environment_telemetry import EnvironmentTelemetryData
from plants_system.smart_objects.devices.tank_monitoring import TankMonitoring
from plants_system.smart_objects.devices.water_metering import WaterMetering

class PlantDescriptor:
    def __init__(self, species, plant_id):
        self.plant_id = plant_id
        self.species = species
        self.devices = [
            EnvironmentTelemetryData(self.plant_id),
            TankMonitoring(self.plant_id),
            WaterMetering(self.plant_id)
        ]
    
        
    def to_json(self):
        return json.dumps({
            "plant_id": self.plant_id,
            "species": self.species,
            "sensors": [sensor.type for sensor in self.devices if hasattr(sensor, 'type')],
            "actuators": [actuator.type for actuator in self.devices if hasattr(actuator, 'type')]
        })