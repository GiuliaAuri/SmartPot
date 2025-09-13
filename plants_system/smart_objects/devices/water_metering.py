
import logging
from plants_system.smart_objects.actuators.irrigation_actuator import IrrigationActuator
from plants_system.smart_objects.models.Device import Device
from plants_system.smart_objects.sensors.water_flow_sensor import WaterFlowSensor

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("water_metering")

class WaterMetering(Device):

    def __init__(self, plant_id: str):
        super().__init__(
            plant_id,
            "water_metering",
            sensors=[WaterFlowSensor(plant_id, initial_value=0.0, unit="l/s", min_value=0, max_value=5, device="water_metering", is_real=False)],
            actuators=[IrrigationActuator(plant_id, device="water_metering", is_real=False)]
        )
        