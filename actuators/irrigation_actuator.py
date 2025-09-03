
from model.SwitchActuator import SwitchActuator


class IrrigationActuator(SwitchActuator):
    def __init__(self, plant_id:str):
        super().__init__(plant_id=plant_id, device="irrigation_actuator")