
import logging
from plants_system.smart_objects.models.Device import Device
from plants_system.smart_objects.sensors.level_tank_sensor import LevelTankSensor

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("tank_monitoring")

class TankMonitoring(Device):

    def __init__(self, plant_id: str):
        super().__init__(
            plant_id, 
            "tank_monitoring", 
            sensors=[LevelTankSensor(plant_id, initial_value=1.0, unit="l", min_value=0.0, max_value=1.0, device="tank_monitoring")]
            )
        
