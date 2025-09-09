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
    """
    Classe principale per la gestione delle piante IoT nel sistema.
    
    Questa classe coordina l'intero sistema delle piante intelligenti:
    - Caricamento delle configurazioni delle piante
    - Avvio dei producer per la pubblicazione dei dati telemetrici
    - Avvio dei consumer per la ricezione dei comandi
    - Gestione dei thread per l'elaborazione parallela
    - Controllo del ciclo di vita dell'applicazione
    """
    def __init__(self, config_path):
        self.plants = PlantFactory.create_plants_from_json(config_path)
        self.threads = []
        self.producers = []
        self.consumers = []

    def start(self):
        """
        Avvia i producer e i consumer per ogni pianta.
        """
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
        """
        Interrompe i producer e i consumer e attende la terminazione dei thread.
        """
        for producer in self.producers:
            producer.stop()
        for consumer in self.consumers:
            consumer.stop()
        for thread in self.threads:
            thread.join()

if __name__ == "__main__":
    """
    Entry point principale dell'applicazione delle piante.
    
    Crea un'istanza della classe Plants, avvia tutti i producer e consumer
    e mantiene l'applicazione in esecuzione fino a quando non viene ricevuto
    un segnale di interruzione (Ctrl+C).
    """
    manager = Plants("plants_system/smart_objects/resources/plants_config.json")
    manager.start()
    try:
        while True:
            time.sleep(2)  
    except KeyboardInterrupt:
        print("Stopping all threads...")
        manager.stop()