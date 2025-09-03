import time
import sys
import os
import logging
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from process.mqtt_sensor_manager import MqttSensorManager
from process.mqtt_actuator_manager import MqttActuatorManager
from model.plant_descriptor import PlantDescriptor
from model.SwitchActuator import SwitchActuator
from model.Sensor import Sensor
from sensor.humidity_sensor import HumiditySensor
from sensor.temperature_sensor import TemperatureSensor

class PlantServer:
    def __init__(self, plants: list[PlantDescriptor]):
        
        self.plants = plants
        self.sensor_managers = {}
        self.actuator_managers = {}

        
        for plant in self.plants:
            self.sensor_managers[plant.plant_id] = MqttSensorManager(plant)
            self.actuator_managers[plant.plant_id] = MqttActuatorManager(plant)

    def run(self, interval=3.0):
        try:
            print("Plants Server running... ")
            while True:
                for plant_id, sensor_manager in self.sensor_managers.items():
                    sensor_manager.publish_telemetry()

                time.sleep(interval)
        except KeyboardInterrupt:
            print("Stopping Plant Server...")
            self.stop()

    def stop(self):
        for sm in self.sensor_managers.values():
            sm.stop()
        for am in self.actuator_managers.values():
            am.stop()


# --- Esempio di utilizzo multi-pianta ---

if __name__ == "__main__":
    #TODO sostituzione: la creazione delle piante da fare in una classe specifica
    # Creazione pianta 1
    plant1 = PlantDescriptor(
        species="cactus",
        sensors=[
            TemperatureSensor(initial_value=20.0, unit="°C", min_value=0.0, max_value=50.0, device="environment_telemetry"),
            HumiditySensor(initial_value=50.0, unit="%", min_value=0.0, max_value=100.0, device="environment_telemetry")
        ],
        actuators=[SwitchActuator("pump01")]
    )

    # Creazione pianta 2
    plant2 = PlantDescriptor(
        species="fico",
        sensors=[
            TemperatureSensor(initial_value=20.0, unit="°C", min_value=0.0, max_value=50.0, device="environment_telemetry"),
            HumiditySensor(initial_value=50.0, unit="%", min_value=0.0, max_value=100.0, device="environment_telemetry")
        ],
        actuators=[SwitchActuator("fan01"), SwitchActuator("heater01")]
    )

    # Lista di piante gestite dal server
    plants = [plant1, plant2]

    # Avvio server
    server = PlantServer(plants)
    server.run(interval=5.0)
