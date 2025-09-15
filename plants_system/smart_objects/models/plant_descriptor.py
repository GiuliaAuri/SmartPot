import json
from plants_system.smart_objects.devices.environment_telemetry import EnvironmentTelemetryData
from plants_system.smart_objects.devices.tank_monitoring import TankMonitoring
from plants_system.smart_objects.devices.water_metering import WaterMetering

class PlantDescriptor:
    def __init__(self, species, plant_id, devices=None):
        self.plant_id = plant_id
        self.species = species
        #TODO: deve creare i direttamente i sensori e attuatori

        
        if devices is not None:
            self.devices = devices
        else:
            self.devices = [
                EnvironmentTelemetryData(self.plant_id),
                TankMonitoring(self.plant_id),
                WaterMetering(self.plant_id)
            ]
    
        
    def to_json(self):
        # Estrai tutti i sensori da tutti i dispositivi
        all_sensors = []
        all_actuators = []
        
        for device in self.devices:
            all_sensors.extend([sensor.type for sensor in device.sensors])
            all_actuators.extend([actuator.type for actuator in device.actuators])
        
        return json.dumps({
            "plant_id": self.plant_id,
            "species": self.species,
            "sensors": all_sensors,
            "actuators": all_actuators
        })