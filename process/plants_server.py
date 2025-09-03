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
from sensors.humidity_sensor import HumiditySensor
from sensors.temperature_sensor import TemperatureSensor

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
    from device.tank_monitoring import TankMonitoring
    from device.water_metering import WaterMetering

    # Test TankMonitoring
    tank_monitor = TankMonitoring(plant_id="plant01")
    tank_monitor.update_measurements()
    print("TankMonitoring JSON:", tank_monitor.to_json())

    # Test WaterMetering
    water_meter = WaterMetering(plant_id="plant01")
    water_meter.update_measurements()
    print("WaterMetering JSON:", water_meter.to_json())

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
    plant3 = PlantDescriptor(
        species="cactus",
        sensors=[
            tank_monitor.level_tank,
            water_meter.water_flow
        ],
        actuators=[
            water_meter.irrigation
        ]
    )

    # Lista di piante gestite dal server
    plants = [plant1, plant2, plant3]

    # Avvio server
    server = PlantServer(plants)
    server.run(interval=5.0)
