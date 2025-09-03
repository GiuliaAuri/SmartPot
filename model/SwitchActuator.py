
class SwitchActuator:

    def __init__(self, type: str):
        self.status = False
        self.type = type

    def change_status(self):
        self.status = not self.status
