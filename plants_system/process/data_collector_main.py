import sys
import os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '../..')))

import threading
from plants_system.smart_objects.resources.factory_plants import PlantFactory
from plants_system.process.data_collector_consumer import DataCollectorConsumer

class Main:
    def __init__(self, config_path):
        self.plants = PlantFactory.create_plants_from_json(config_path)
        self.threads = []
        self.consumers = []

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
    manager = Main("plants_system/smart_objects/resources/plants_config.json")
    manager.start()
    try:
        while True:
            pass  
    except KeyboardInterrupt:
        print("Stopping all threads...")
        manager.stop()