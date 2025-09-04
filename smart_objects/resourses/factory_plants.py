import json
from smart_objects.model.plant_descriptor import PlantDescriptor
from smart_objects.sensors.temperature_sensor import TemperatureSensor
from smart_objects.sensors.humidity_sensor import HumiditySensor
from smart_objects.device.tank_monitoring import TankMonitoring
from smart_objects.device.water_metering import WaterMetering
from smart_objects.device.environment_telemetry import EnvironmentTelemetryData
from smart_objects.model.SwitchActuator import SwitchActuator

class PlantFactory:
    @staticmethod
    def create_plants_from_json(json_path):
        with open(json_path, "r") as f:
            plants_data = json.load(f)
        plants = []
        for pdata in plants_data:
            # Passa il plant_id dal JSON se presente
            plant = PlantDescriptor(
                species=pdata["species"],
                plant_id=pdata.get("plant_id")
            )
            plants.append(plant)
        return plants