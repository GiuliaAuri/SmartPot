#TODO è da inserire qua la lista di attuatori e sensori, o in plant_descripto?
import json
import time
import logging
from actuators.irrigation_actuator import IrrigationActuator
from sensors.water_flow_sensor import WaterFlowSensor

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("water_metering")

class WaterMetering:

    def __init__(self, plant_id: str):
        self.plant_id = plant_id
        self.device = "water_metering"
        self.water_flow=WaterFlowSensor(initial_value=0.0, unit="l/s", min_value=0, max_value=5, device=self.device)
        self.irrigation=IrrigationActuator()
        self.timestamp = int(time.time())

    def update_measurements(self):
        self.water_flow.update()
        self.timestamp = int(time.time())
        logger.info(f"Updated: {self.to_json()}")

    def to_json(self):
        return json.dumps(self, default=lambda o: o.__dict__)