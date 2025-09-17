import logging
import random
import time
from smart_objects.models.Sensor import Sensor

class HumiditySensor(Sensor[float]):
    def __init__(self, plant_id: str, initial_value: float, unit: str, min_value: float, max_value: float, device: str, is_real: bool = False):
        super().__init__(plant_id, initial_value, unit, min_value, max_value, "humidity", device)
    
    def calculate_relative_percentage(self, value: float) -> float:
        """Calcola la percentuale relativa tra min e max per un sensore."""
        
        # Calcola la percentuale relativa
        if self.min_value == self.max_value:
            return 50.0  # Evita divisione per zero
        
        # Clamp il valore tra min e max
        clamped_value = max(self.min_value, min(self.max_value, value))
        
        # Per sensori di umidità: valore basso = umidità alta (terreno umido)
        # Valore alto = umidità bassa (terreno secco)
        # Formula: 100 -((valore - min) / (max - min)) * 100
        percentage = 100 -((clamped_value - self.min_value) / (self.max_value - self.min_value)) * 100
        return percentage
