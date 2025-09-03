
class SwitchActuator:

    def __init__(self, device:str):
        self.status = False
        self.device = device

    def change_status(self):
        self.status = not self.status
