from smart_objects.models.SwitchActuator import SwitchActuator


class IrrigationActuator(SwitchActuator):
    def __init__(self, plant_id:str, device:str="irrigation"):
        super().__init__(plant_id=plant_id, type="irrigation", device=device)


