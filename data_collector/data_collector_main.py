import logging
import sys
import os

# Aggiungi il path per importare i moduli del progetto
# data_collector_main.py è in data_collector/, quindi devo salire solo di 1 livello
project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
sys.path.insert(0, project_root)


import time
import threading
from data_collector.factory.factory import Factory
from data_collector.data_collector_consumer import DataCollectorConsumer
#from plants_system.smart_objects.resources.plant_info_consumer import PlantInfoConsumer

#FILENAME="cloud_simulator/plants.json"
PATH="cloud_simulator/plants_log/"
#PATH="data_collector/plants_log/"

class Main:
    """
    Classe principale per la gestione dei consumer dei dati delle piante.
    
    Questa classe si occupa di eseguire la discovery delle piante,
    creare i consumer per ogni pianta e avviare i thread per il consumo dei dati.
    """
    def __init__(self, config_path):
        #TODO: devo fare la discovery delle piante come??
        print("🔧 Creazione plant descriptors...")
        try:
            self.plants = Factory.create_plant_descriptor()
            print(f"✅ Creati {len(self.plants)} plant descriptors")
            for plant in self.plants:
                print(f"   - {plant.plant_id} ({plant.species})")
        except Exception as e:
            print(f"❌ Errore creazione plant descriptors: {e}")
            import traceback
            traceback.print_exc()
            self.plants = []
        
        self.threads = []
        self.consumers = []

   
    def start(self):
        """
        Avvia i consumer per ogni pianta.
        """
        print(f"🚀 Avvio {len(self.plants)} consumer...")
        for i, plant in enumerate(self.plants):
            print(f"🚀 Avvio consumer {i+1}/{len(self.plants)} per {plant.plant_id}")
            try:
                consumer = DataCollectorConsumer(plant, PATH)
                t = threading.Thread(target=consumer.run)
                t.start()
                self.threads.append(t)
                self.consumers.append(consumer)
                print(f"   ✅ Consumer {plant.plant_id} avviato")
            except Exception as e:
                print(f"   ❌ Errore avvio consumer {plant.plant_id}: {e}")
                import traceback
                traceback.print_exc()

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
    
    # Verifica che il file di configurazione esista
    config_file = "data_collector/factory/plants_config.json"
    if not os.path.exists(config_file):
        print(f"❌ File di configurazione non trovato: {config_file}")
        sys.exit(1)
    
    print(f"✅ File di configurazione trovato: {config_file}")
    
    print("🏗️ Creazione Main...")
    manager=Main(config_file)
    print("🚀 Avvio consumer...")
    # Avvio dei consumer
    manager.start()
    print("⏳ Sistema in esecuzione...")
    try:
        while True:
            time.sleep(1)  # Sleep per evitare CPU al 100%
    except KeyboardInterrupt:
        print("\n🛑 Interruzione da tastiera (Ctrl+C)")
        print("Stopping all threads...")
        manager.stop()
    except Exception as e:
        print(f"\n❌ Errore durante l'esecuzione: {e}")
        import traceback
        traceback.print_exc()
        print("Stopping all threads...")
        manager.stop()