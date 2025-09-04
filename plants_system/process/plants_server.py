import time
import sys
import os
import logging

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '../..')))
from plants_system.process.policy_manager import PolicyManager
from plants_system.smart_objects.resources.factory_plants import PlantFactory
from plants_system.process.mqtt_sensor_manager import MqttSensorManager
from plants_system.process.mqtt_actuator_manager import MqttActuatorManager
from plants_system.smart_objects.models.plant_descriptor import PlantDescriptor
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("plant_server")

class PlantServer:
    def __init__(self, plants: list[PlantDescriptor], policy_manager=None):
        self.plants = plants
        self.sensor_managers = {}
        self.actuator_managers = {}
        self.policy_manager = policy_manager
        for plant in self.plants:
            self.sensor_managers[plant.plant_id] = MqttSensorManager(plant)
            self.actuator_managers[plant.plant_id] = MqttActuatorManager(plant)

    def run(self, interval=3.0):
        try:
            logging.info("Plants Server running...")
            while True:
                for plant in self.plants:
                    self.sensor_managers[plant.plant_id].publish_telemetry()
                    #for sensor in plant.sensors:
                    #    sensor.update()
                    if self.policy_manager:
                        self.policy_manager.evaluate(plant)

                time.sleep(interval)
        except KeyboardInterrupt:
            logging.info("Stopping Plant Server...")
            self.stop()

    def stop(self):
        for sm in self.sensor_managers.values():
            sm.stop()
        for am in self.actuator_managers.values():
            am.stop()



if __name__ == "__main__":
    plants = PlantFactory.create_plants_from_json("plants_system/smart_objects/resources/plants_config.json")
    policy_manager = PolicyManager("plants_system/smart_objects/resources/policies_conf.json")
    server = PlantServer(plants, policy_manager=policy_manager)
    server.run(interval=10.0)

