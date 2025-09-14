from abc import ABC
import logging
from bridge.bridge_Serial import Bridge

class SwitchActuator(ABC):

    def __init__(self, plant_id:str, type:str, device:str, is_real: bool):
        self.plant_id = plant_id
        self.status = False
        self.type = type
        self.device = device
        self.is_real = is_real
        self.bridge_serial = Bridge()  # Usa l'istanza singleton condivisa
        
    def change_status(self):
        self.status = not self.status
        
    def handle_command(self, command: str):
        if self.is_real:
            self.handle_command_real(command)
        else:
            self.handle_command_simulated(command)

    def handle_command_real(self, command: str):
        self.bridge_serial.send_actuator_command(self.type, command)
        logging.info(f"Comando reale inviato per {self.type}: {command}")

    
    def handle_command_simulated(self, command: str):
        if command.upper().startswith("ACTIVATE"):
            self.status = True
            logging.info(f"{self.device} -> switched ON")
        elif command.upper().startswith("DEACTIVATE"):
            self.status = False
            logging.info(f"{self.device} -> switched OFF")
        else:
            logging.warning(f"{self.device} -> unknown command: {command}")

