import logging
import sys
import os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '../..')))
import time
import threading
from plants_system.smart_objects.resources.factory_plants import PlantFactory
from plants_system.process.data_collector_consumer import DataCollectorConsumer

from plants_system.smart_objects.resources.plant_info_consumer import PlantInfoConsumer

class Main:
    def __init__(self, config_path):
        self.plants = PlantFactory.create_plants_from_json(config_path)
        self.threads = []
        self.consumers = []

    def discover_plants(self, filename, discovery_time):
        """
        Esegue la discovery delle piante tramite PlantInfoConsumer per discovery_time secondi.
        """
        plant_info_discoverer = PlantInfoConsumer(filename)
        plant_info_discoverer.run()
        time.sleep(discovery_time)
        if hasattr(plant_info_discoverer, "stop"):
            plant_info_discoverer.stop()
        else:
            logging.warning("PlantInfoConsumer has no stop method")

    def start(self):
        for plant in self.plants:
            consumer = DataCollectorConsumer(plant)
            t = threading.Thread(target=consumer.run)
            t.start()
            self.threads.append(t)
            self.consumers.append(consumer)

    def stop(self):
        for consumer in self.consumers:
            if hasattr(consumer, "stop"):
                consumer.stop()
        for t in self.threads:
            t.join()

if __name__ == "__main__":
    manager = Main("plants_system/smart_objects/resources/plants_discovery.json")
    # Discovery delle piante per 20 secondi
    manager.discover_plants("plants_system/smart_objects/resources/plants_discovery.json", 20)
    # Avvio dei consumer
    manager.start()
    try:
        while True:
            pass
    except KeyboardInterrupt:
        print("Stopping all threads...")
        manager.stop()