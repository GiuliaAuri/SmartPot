
class SwitchActuator:

    def __init__(self, plant_id:str, device:str):
        self.plant_id = plant_id
        self.status = False
        self.device = device

    def change_status(self):
        self.status = not self.status
