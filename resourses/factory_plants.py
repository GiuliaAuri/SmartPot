import json
from model.plant_descriptor import PlantDescriptor
from sensors.temperature_sensor import TemperatureSensor
from sensors.humidity_sensor import HumiditySensor
from device.tank_monitoring import TankMonitoring
from device.water_metering import WaterMetering
from device.environment_telemetry import EnvironmentTelemetryData
from model.SwitchActuator import SwitchActuator

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