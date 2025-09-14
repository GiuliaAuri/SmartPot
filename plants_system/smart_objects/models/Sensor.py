from abc import ABC, abstractmethod
import logging
import random
import time
from typing import Generic, TypeVar
import json
from bridge.bridge_Serial import Bridge

T = TypeVar('T')


class Sensor(ABC, Generic[T]):
    def __init__(self, plant_id: str, initial_value: T, unit:str, min_value: T, max_value: T, type:str, device:str, is_real: bool):
        self.plant_id = plant_id
        self.value = initial_value
        self.unit = unit
        self.min_value = min_value
        self.max_value = max_value
        self.type = type
        self.device = device
        self.timestamp = 0
        self.is_real = is_real
        self.bridge_serial = None  # Inizializzato solo quando necessario

    def update(self):
        if self.is_real:
            self.update_real()
        else:
            self.update_simulated()

    def update_real(self):
        # Inizializza il Bridge solo quando necessario
        if self.bridge_serial is None:
            try:
                self.bridge_serial = Bridge()
            except Exception as e:
                logging.warning(f"Impossibile inizializzare Bridge per sensore {self.type}: {e}")
                return
        
        # Debug: mostra tutti i valori disponibili nel Bridge
        all_values = self.bridge_serial.get_sensor_value(None)
        logging.debug(f"Bridge values disponibili per {self.plant_id}: {all_values}")
        
        sensor_value = self.bridge_serial.get_sensor_value(self.type)
        logging.debug(f"Valore richiesto per {self.type}: {sensor_value}")
        
        if sensor_value is not None:
            self.value = sensor_value
            self.timestamp = int(time.time())
            logging.info(f"Updated real {self.type} measurement: {self.value} {self.unit} at {self.timestamp} - plant: {self.plant_id}")
        else:
            logging.warning(f"Nessun valore disponibile per sensore {self.type} - plant: {self.plant_id}")

    def update_simulated(self):
        self.value = round(random.uniform(self.min_value, self.max_value),1)
        self.timestamp = int(time.time())
        logging.info(f"Updated {self.type} measurement: {self.value} {self.unit} at {self.timestamp} - plant: {self.plant_id}")

    def to_json(self):
        """
        Converte il sensore in formato JSON.
        
        Returns:
            Stringa JSON contenente tutte le proprietà del sensore
        """
        return json.dumps({
            "type": self.type,
            "value": self.value,
            "device": self.device,
            "unit": self.unit,
            "timestamp": self.timestamp,
            "plant_id": self.plant_id
        })
    
    def _set_max(self, max_value: T):
        self.max_value = max_value
    
    def _set_min(self, min_value: T):
        self.min_value = min_value
    
    def _set_unit(self, unit: str):
        self.unit = unit

    def _set_type(self, type: str):
        self.type = type

    def _set_device(self, device: str):
        self.device = device