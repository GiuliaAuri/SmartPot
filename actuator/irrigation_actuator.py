
from model.SwitchActuator import SwitchActuator


class IrrigationActuator(SwitchActuator):
    def __init__(self):
        super().__init__(type="irrigation")