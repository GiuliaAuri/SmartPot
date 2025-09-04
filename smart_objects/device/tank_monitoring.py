import json
import time
import logging
from smart_objects.sensors.level_tank_sensor import LevelTankSensor

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("tank_monitoring")

class TankMonitoring:

    def __init__(self, plant_id: str):
        self.plant_id = plant_id
        self.device = "tank_monitoring"
        self.level_tank=LevelTankSensor(self.plant_id, initial_value=1.0, unit="l", min_value=0.0, max_value=1.0, device=self.device)
        self.timestamp = int(time.time())

    def update_measurements(self):
        self.level_tank.update()
        self.timestamp = int(time.time())
        logger.info(f"Updated: {self.to_json()}")

    def to_json(self):
        return json.dumps(self, default=lambda o: o.__dict__)
