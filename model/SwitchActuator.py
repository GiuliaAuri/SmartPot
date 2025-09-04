import logging

class SwitchActuator:

    def __init__(self, plant_id:str, type:str):
        self.plant_id = plant_id
        self.status = False
        self.type = type

    def change_status(self):
        self.status = not self.status
        
    def handle_command(self, command: str):
        if command.upper() == "ON":
            self.status = True
            logging.info(f"{self.device} -> switched ON")
        elif command.upper() == "OFF":
            self.status = False
            logging.info(f"{self.device} -> switched OFF")
        else:
            logging.warning(f"{self.device} -> unknown command: {command}")

