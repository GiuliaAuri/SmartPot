#!/usr/bin/env python3
"""
Test per verificare la coerenza del sistema Producer-Consumer.
"""

import sys
import os
import time

# Aggiungi il path per importare i moduli del progetto
project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), '.'))
sys.path.insert(0, project_root)

from data_collector.factory.factory import Factory
from data_collector.data_collector_producer import DataCollectorProducer
import threading

def test_producer_actuator_saving():
    """Test del salvataggio delle azioni degli attuatori nel Producer."""
    
    print("🧪 Test Producer - Salvataggio Azioni Attuatori")
    print("=" * 50)
    
    try:
        # Crea plant descriptor
        plants = Factory.create_plant_descriptor()
        if not plants:
            print("❌ Nessuna pianta creata")
            return
        
        plant = plants[0]
        print(f"🌱 Pianta test: {plant.plant_id} ({plant.species})")
        
        # Test comandi
        test_commands = [
            "start",
            "stop", 
            "Activate irrigation",
            "Deactivate irrigation"
        ]
        
        for command in test_commands:
            print(f"\n📤 Test comando: '{command}'")
            
            # Crea producer
            producer = DataCollectorProducer(plant, command)
            
            # Esegui comando
            producer.run()
            
            print(f"✅ Comando '{command}' eseguito")
            
            # Pausa tra i comandi
            time.sleep(1)
        
        print("\n📁 Verifica file JSON creato...")
        
        # Verifica che il file JSON sia stato creato/aggiornato
        json_file = f"cloud_simulator/plants_log/{plant.plant_id}.json"
        if os.path.exists(json_file):
            print(f"✅ File JSON trovato: {json_file}")
            
            # Leggi e mostra il contenuto
            import json
            with open(json_file, 'r') as f:
                data = json.load(f)
            
            if 'actuators' in data and 'irrigation' in data['actuators']:
                actions = data['actuators']['irrigation']
                print(f"📊 Azioni irrigazione salvate: {len(actions)}")
                for i, action in enumerate(actions[-3:]):  # Mostra ultime 3
                    print(f"   {i+1}. {action['action']} - {action['datetime']}")
            else:
                print("⚠️ Nessuna azione di irrigazione trovata")
        else:
            print(f"❌ File JSON non trovato: {json_file}")
        
        print("\n🎯 Test completato!")
        
    except Exception as e:
        print(f"❌ Errore durante il test: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    test_producer_actuator_saving()
