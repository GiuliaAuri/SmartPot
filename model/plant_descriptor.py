import json
import uuid

from model import Sensor, SwitchActuator, SwitchActuator


class PlantDescriptor:
    def __init__(self, species, plant_id):
        self.plant_id = plant_id
        self.species = species
        # Crea dispositivi base
        from device.environment_telemetry import EnvironmentTelemetryData
        from device.tank_monitoring import TankMonitoring
        from device.water_metering import WaterMetering
        self.env_telemetry = EnvironmentTelemetryData(self.plant_id)
        self.tank_monitor = TankMonitoring(self.plant_id)
        self.water_meter = WaterMetering(self.plant_id)
        # Sensori di base
        self.sensors = [
            self.env_telemetry.temperature,
            self.env_telemetry.humidity,
            self.env_telemetry.lightness,
            self.env_telemetry.batteryLevel,
            self.tank_monitor.level_tank,
            self.water_meter.water_flow
        ]
        # Attuatori di base
        self.actuators = [self.water_meter.irrigation]

    def to_json(self):
        return json.dumps({
            "plant_id": self.plant_id,
            "species": self.species,
            "sensors": [sensor.type for sensor in self.sensors],
            "actuators": [actuator.type for actuator in self.actuators]
        })