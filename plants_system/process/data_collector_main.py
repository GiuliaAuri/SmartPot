import logging
import sys
import os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '../..')))
import time
import threading
from plants_system.smart_objects.resources.factory_plants import PlantFactory
from plants_system.process.data_collector_consumer import DataCollectorConsumer
from plants_system.smart_objects.resources.plant_info_consumer import PlantInfoConsumer

FILENAME="cloud_simulator/plants.json"
PATH="cloud_simulator/plants_log/"

class Main:
    """
    Classe principale per la gestione dei consumer dei dati delle piante.
    
    Questa classe si occupa di eseguire la discovery delle piante,
    creare i consumer per ogni pianta e avviare i thread per il consumo dei dati.
    """
    def __init__(self, config_path):
        self.discover_plants(config_path, 10)
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
        """
        Avvia i consumer per ogni pianta.
        """
        for plant in self.plants:
            consumer = DataCollectorConsumer(plant, PATH)
            t = threading.Thread(target=consumer.run)
            t.start()
            self.threads.append(t)
            self.consumers.append(consumer)

    def stop(self):
        """
        Interrompe i consumer e attende la terminazione dei thread.
        """
        for consumer in self.consumers:
            if hasattr(consumer, "stop"):
                consumer.stop()
        for t in self.threads:
            t.join()

if __name__ == "__main__":
    """
    Entry point principale dell'applicazione data collector.
    
    Crea un'istanza della classe Main, avvia tutti i consumer e mantiene
    l'applicazione in esecuzione fino a quando non viene ricevuto un
    segnale di interruzione (Ctrl+C).
    """
    manager = Main(FILENAME)
    # Avvio dei consumer
    manager.start()
    try:
        while True:
            pass
    except KeyboardInterrupt:
        print("Stopping all threads...")
        manager.stop()