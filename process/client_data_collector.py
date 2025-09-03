import sys
import os
import logging
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from process.mqtt_sensor_manager import MqttSensorManager
from process.mqtt_actuator_manager import MqttActuatorManager
from model.plant_descriptor import PlantDescriptor
from model.SwitchActuator import SwitchActuator
from model.Sensor import Sensor
from sensors.temperature_sensor import TemperatureSensor
from sensors.humidity_sensor import HumiditySensor

class PlantClient:
    def __init__(self, plants):
        """
        plants: lista di PlantDescriptor
        """
        self.plants = plants
        self.sensor_managers = {}
        self.actuator_managers = {}

        # Inizializza manager per ogni pianta
        for plant in self.plants:
            self.sensor_managers[plant.plant_id] = MqttSensorManager(plant)
            self.actuator_managers[plant.plant_id] = MqttActuatorManager(plant)

    def send_command(self, plant_id: str, actuator_name: str, command: str):
        """
        Invia un comando a un attuatore specifico di una pianta
        """
        plant = next((p for p in self.plants if p.plant_id == plant_id), None)
        if not plant:
            print(f"Pianta {plant_id} non trovata.")
            return

        actuator = next((a for a in plant.actuators if a.device == actuator_name), None)
        if not actuator:
            print(f"Attuatore {actuator_name} non trovato nella pianta {plant_id}.")
            return

        self.actuator_managers[plant_id].send_command(command, actuator)
        print(f"Comando inviato a {actuator_name} della pianta {plant_id}: {command}")

    def stop(self):
        for sm in self.sensor_managers.values():
            sm.stop()
        for am in self.actuator_managers.values():
            am.stop()


# --- Esempio di utilizzo multi-pianta ---

if __name__ == "__main__":
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
    # Sostituisci Sensor("soil_moisture") con una classe concreta, ad esempio SoilMoistureSensor
    # from sensor.soil_moisture_sensor import SoilMoistureSensor
    plant2 = PlantDescriptor(
        species="fico",
        sensors=[
            TemperatureSensor(initial_value=20.0, unit="°C", min_value=0.0, max_value=50.0, device="environment_telemetry"),
            HumiditySensor(initial_value=50.0, unit="%", min_value=0.0, max_value=100.0, device="environment_telemetry")
        ],
        actuators=[SwitchActuator("fan01"), SwitchActuator("heater01")]
    )

    plants = [plant1, plant2]

    # Avvio client
    client = PlantClient(plants)

    try:
        print("Plant Client running. Digita 'exit' per uscire.")
        while True:
            cmd_input = input("Inserisci comando (formato: plant_id actuator command): ")
            if cmd_input.lower() == "exit":
                break

            parts = cmd_input.strip().split()
            if len(parts) != 3:
                print("Formato comando errato. Esempio corretto: plant01 pump01 ON")
                continue

            plant_id, actuator_name, command = parts
            client.send_command(plant_id, actuator_name, command)

    except KeyboardInterrupt:
        pass
    finally:
        print("Stopping Plant Client...")
        client.stop()

    sensors=[
        TemperatureSensor(initial_value=20.0, unit="°C", min_value=0.0, max_value=50.0, device="environment_telemetry"),
        HumiditySensor(initial_value=50.0, unit="%", min_value=0.0, max_value=100.0, device="environment_telemetry")
    ]
