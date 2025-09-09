import json
from plants_system.smart_objects.models.plant_descriptor import PlantDescriptor
from plants_system.smart_objects.sensors.temperature_sensor import TemperatureSensor
from plants_system.smart_objects.sensors.humidity_sensor import HumiditySensor
from plants_system.smart_objects.devices.tank_monitoring import TankMonitoring
from plants_system.smart_objects.devices.water_metering import WaterMetering
from plants_system.smart_objects.devices.environment_telemetry import EnvironmentTelemetryData
from plants_system.smart_objects.models.SwitchActuator import SwitchActuator

class PlantFactory:
    """
    Factory per la creazione di piante da file JSON.
    
    Questa classe permette di creare oggetti PlantDescriptor da file JSON,
    contenenti informazioni base sulla pianta come nome e tipo.
    """
    @staticmethod
    def create_plants_from_json(json_path):
        with open(json_path, "r") as f:
            plants_data = json.load(f)
        plants = []
        for pdata in plants_data:
            plant = PlantDescriptor(
                species=pdata["species"],
                plant_id=pdata.get("plant_id")
            )
            plants.append(plant)
        return plants