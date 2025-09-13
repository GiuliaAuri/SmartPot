from plants_system.smart_objects.models.SwitchActuator import SwitchActuator


class IrrigationActuator(SwitchActuator):
    def __init__(self, plant_id:str, device:str="irrigation", is_real: bool = False):
        super().__init__(plant_id=plant_id, type="irrigation", device=device, is_real=is_real)
      


