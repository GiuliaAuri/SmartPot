from abc import ABC

class SwitchActuator(ABC):

    def __init__(self, plant_id:str, type:str, device:str):
        self.plant_id = plant_id
        self.status = False
        self.type = type
        self.device = device
        
        