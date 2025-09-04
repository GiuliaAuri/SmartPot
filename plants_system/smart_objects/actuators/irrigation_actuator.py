from plants_system.smart_objects.models.SwitchActuator import SwitchActuator


class IrrigationActuator(SwitchActuator):
    def __init__(self, plant_id:str):
        super().__init__(plant_id=plant_id, type="irrigation_actuator", device="irrigation_actuator")
      


