import sys
import os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '../..')))
import signal
import time
import threading
from plants_system.smart_objects.resources.factory_plants import PlantFactory
from plants_system.process.plant_producer import PlantProducer
from plants_system.process.plant_consumer import PlantConsumer

class Plants:
    def __init__(self, config_path):
        #TODO creazione delle piante NON a partire dal json
        self.plants = PlantFactory.create_plants_from_json(config_path)
        self.threads = []
        self.producers = []
        self.consumers = []

    def start(self):
        for plant in self.plants:
            producer = PlantProducer(plant)
            consumer = PlantConsumer(plant)
            t_producer = threading.Thread(target=producer.run)
            t_consumer = threading.Thread(target=consumer.run)
            t_producer.start()
            t_consumer.start()
            self.threads.extend([t_producer, t_consumer])
            self.producers.append(producer)
            self.consumers.append(consumer)

    def stop(self):
        # Chiamata ai metodi stop di tutti i producer e consumer
        for producer in self.producers:
            producer.stop()
        for consumer in self.consumers:
            consumer.stop()
        # Poi aspetta la fine dei thread
        for thread in self.threads:
            thread.join()

if __name__ == "__main__":
    manager = Plants("plants_system/smart_objects/resources/plants_config.json")
    manager.start()
    try:
        while True:
            time.sleep(2)  
    except KeyboardInterrupt:
        print("Stopping all threads...")
        manager.stop()