import sys
import os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '../..')))
import signal
import time
import threading
import logging
from typing import List, Callable, Any
from plants_system.smart_objects.resources.factory_plants import PlantFactory
from plants_system.process.plant_producer import PlantProducer
from plants_system.process.plant_consumer import PlantConsumer
from bridge.bridge_Serial import Bridge

# Configurazione logging
logging.basicConfig(level=logging.DEBUG, format='%(asctime)s - %(levelname)s - %(message)s')

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
        self.producers = []
        self.consumers = []
        self.arduino_bridge = Bridge()  # Inizializza il Bridge Arduino
        
        # Gestione thread integrata
        self.threads: List[threading.Thread] = []
        self.running = False
        self.shutdown_event = threading.Event()
        self.arduino_thread = None
        self.arduino_connected = False

    def start(self):
        """
        Avvia i producer e i consumer per ogni pianta e il Bridge Arduino.
        """
        logging.info(f"Avvio sistema per {len(self.plants)} piante...")
        
        # Crea producer e consumer per ogni pianta
        for plant in self.plants:
            producer = PlantProducer(plant)
            consumer = PlantConsumer(plant)
            
            # Crea thread per producer e consumer
            producer_thread = threading.Thread(
                target=producer.run,
                name=f"Producer-{plant.plant_id}"
            )
            consumer_thread = threading.Thread(
                target=consumer.run,
                name=f"Consumer-{plant.plant_id}"
            )
            
            # Avvia i thread
            producer_thread.start()
            consumer_thread.start()
            
            # Aggiungi ai thread da gestire
            self.threads.extend([producer_thread, consumer_thread])
            self.producers.append(producer)
            self.consumers.append(consumer)
        
        # Avvia il Bridge Arduino
        try:
            if self.arduino_bridge.start():
                self.arduino_thread = self.arduino_bridge  # Il Bridge è un thread
                self.arduino_connected = True
                logging.info("Bridge Arduino avviato correttamente")
            else:
                logging.warning("Bridge Arduino non avviato (porta seriale non disponibile)")
        except Exception as e:
            logging.error(f"Errore avvio Bridge Arduino: {e}")
        
        self.running = True
        
        if self.arduino_connected:
            logging.info("Sistema completo avviato: MQTT + Arduino Bridge")
        else:
            logging.info("Sistema avviato senza Arduino Bridge")

    def stop(self):
        """
        Ferma il sistema completo in modo sicuro.
        """
        logging.info("Inizio shutdown sistema...")
        self.running = False
        self.shutdown_event.set()
        
        # Ferma tutti i producer e consumer
        for producer in self.producers:
            producer.stop()
        for consumer in self.consumers:
            consumer.stop()
        
        # Ferma il Bridge Arduino
        if self.arduino_connected and self.arduino_bridge:
            logging.info("Fermata Bridge Arduino...")
            try:
                self.arduino_bridge.stop()
            except Exception as e:
                logging.error(f"Errore fermata Bridge Arduino: {e}")
        
        # Attendi la terminazione di tutti i thread
        logging.info("Attendo terminazione thread...")
        for thread in self.threads:
            if thread.is_alive():
                logging.info(f"Attendo terminazione thread '{thread.name}'...")
                thread.join(timeout=5.0)
                
                if thread.is_alive():
                    logging.warning(f"Thread '{thread.name}' non terminato entro 5s")
                else:
                    logging.info(f"Thread '{thread.name}' terminato correttamente")
        
        # Attendi la terminazione del thread Arduino
        if self.arduino_thread and self.arduino_thread.is_alive():
            logging.info("Attendo terminazione Bridge Arduino...")
            self.arduino_thread.join(timeout=5.0)
            
            if self.arduino_thread.is_alive():
                logging.warning("Bridge Arduino non terminato entro 5s")
            else:
                logging.info("Bridge Arduino terminato correttamente")
        
        logging.info("Sistema fermato completamente")
    
    def is_running(self) -> bool:
        """Verifica se il sistema è ancora attivo."""
        # Verifica se ci sono thread ancora attivi
        mqtt_threads_active = any(thread.is_alive() for thread in self.threads)
        arduino_active = self.arduino_thread and self.arduino_thread.is_alive()
        
        return self.running and (mqtt_threads_active or arduino_active)
    
    def get_status(self) -> dict:
        """Restituisce lo stato del sistema."""
        active_threads = [thread.name for thread in self.threads if thread.is_alive()]
        
        return {
            "system_running": self.is_running(),
            "plants_count": len(self.plants),
            "producers_count": len(self.producers),
            "consumers_count": len(self.consumers),
            "arduino_connected": self.arduino_connected and (self.arduino_thread and self.arduino_thread.is_alive()),
            "active_threads": active_threads,
            "total_threads": len(self.threads)
        }

if __name__ == "__main__":
    """
    Entry point principale dell'applicazione delle piante.
    
    Crea un'istanza della classe Plants, avvia tutti i producer e consumer
    e mantiene l'applicazione in esecuzione fino a quando non viene ricevuto
    un segnale di interruzione (Ctrl+C).
    """
    manager = Plants("plants_system/smart_objects/resources/plants_config.json")
    
    try:
        # Avvia il sistema
        manager.start()
        
        # Mostra stato iniziale
        status = manager.get_status()
        logging.info(f"Stato sistema: {status}")
        
        # Loop principale con monitoraggio
        while manager.is_running():
            time.sleep(2)
            
            # Mostra stato ogni 30 secondi
            if int(time.time()) % 30 == 0:
                status = manager.get_status()
                logging.info(f"Stato sistema: {status}")
                
    except KeyboardInterrupt:
        logging.info("Ricevuto segnale di interruzione (Ctrl+C)")
    except Exception as e:
        logging.error(f"Errore durante l'esecuzione: {e}")
    finally:
        # Ferma il sistema
        manager.stop()
        
        # Verifica che tutto sia fermato
        if manager.is_running():
            logging.warning("Alcuni thread sono ancora attivi!")
            status = manager.get_status()
            logging.info(f"Thread attivi: {status['active_threads']}")
        else:
            logging.info("Tutti i thread sono stati fermati correttamente")
        
        # Cleanup finale
        manager.threads.clear()
        logging.info("Cleanup completato")