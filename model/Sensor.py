from abc import ABC, abstractmethod
from typing import Generic, TypeVar
import json

T = TypeVar('T')


class Sensor(ABC, Generic[T]):
    def __init__(self, plant_id: str, initial_value: T, unit:str, min_value: T, max_value: T, type:str, device:str):
        self.plant_id = plant_id
        self.value = initial_value
        self.unit = unit
        self.min_value = min_value
        self.max_value = max_value
        self.type = type
        self.device = device
        self.timestamp = 0

    @abstractmethod
    def update(self):
        pass

    def to_json(self):
        return json.dumps(self, default=lambda o: o.__dict__)
    
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