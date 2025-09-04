import sys
import os
import logging

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from smart_objects.resourses.factory_plants import PlantFactory
from process.mqtt_sensor_manager import MqttSensorManager
from process.mqtt_actuator_manager import MqttActuatorManager
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("plant_client")

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
            logger.info(f"Created MqttSensorManager for {plant.plant_id}")
            self.actuator_managers[plant.plant_id] = MqttActuatorManager(plant)
            logger.info(f"Created MqttActuatorManager for {plant.plant_id}")

    def send_command(self, plant_id: str, actuator_name: str, command: str):
        """
        Invia un comando a un attuatore specifico di una pianta
        """
        plant = next((p for p in self.plants if p.plant_id == plant_id), None)
        if not plant:
            logging.error(f"Plant {plant_id} not found.")
            return

        actuator = next((a for a in plant.actuators if a.device == actuator_name), None)
        if not actuator:
            logging.error(f"Actuator {actuator_name} not found in plant {plant_id}.")
            return

        self.actuator_managers[plant_id].send_command(command, actuator)
        logging.info(f"Command sent to {actuator_name} of plant {plant_id}: {command}")

    def stop(self):
        for sm in self.sensor_managers.values():
            sm.stop()
        for am in self.actuator_managers.values():
            am.stop()


if __name__ == "__main__":
    plants = PlantFactory.create_plants_from_json("smart_objects/resourses/plants_config.json")
    
    client = PlantClient(plants)

    try:
        logging.info("Plant Client running...")
        while True:
            cmd_input = input("Enter command (format: plant_id actuator command): ")
            if cmd_input.lower() == "exit":
                break

            parts = cmd_input.strip().split()
            if len(parts) != 3:
                logging.error("Invalid command format. Correct example: plant01 pump01 ON")
                continue

            plant_id, actuator_name, command = parts
            client.send_command(plant_id, actuator_name, command)

    except KeyboardInterrupt:
        pass
    finally:
        logging.info("Stopping Plant Client...")
        client.stop()

