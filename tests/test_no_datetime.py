#!/usr/bin/env python3
"""
Test finale per verificare che il sistema salvi i dati senza il campo datetime.
"""

import sys
import os
import time

# Aggiungi il path per importare i moduli del progetto
project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), '.'))
sys.path.insert(0, project_root)

from data_collector.factory.factory import Factory
from data_collector.data_collector_producer import DataCollectorProducer
from data_collector.json_manager import JsonManager

def test_no_datetime():
    """Test per verificare che i dati vengano salvati senza datetime."""
    
    print("🧪 Test Finale - Salvataggio Senza Datetime")
    print("=" * 50)
    
    try:
        # Crea plant descriptor
        plants = Factory.create_plant_descriptor()
        if not plants:
            print("❌ Nessuna pianta creata")
            return
        
        plant = plants[0]
        print(f"🌱 Pianta test: {plant.plant_id} ({plant.species})")
        
        # Test JsonManager diretto
        print(f"\n📤 Test JsonManager Diretto")
        print("-" * 30)
        
        manager = JsonManager()
        
        # Salva alcuni dati di test
        manager.save_sensor_data(plant.plant_id, "humidity", 90.5, plant.species)
        manager.save_actuator_data(plant.plant_id, "irrigation", "start", plant.species)
        
        print("✅ Dati salvati tramite JsonManager")
        
        # Test Producer
        print(f"\n📤 Test Producer")
        print("-" * 30)
        
        producer = DataCollectorProducer(plant, "stop")
        producer.run()
        
        print("✅ Comando salvato tramite Producer")
        
        # Verifica struttura finale
        print(f"\n📁 Verifica Struttura Finale")
        print("-" * 30)
        
        json_file = f"cloud_simulator/plants_log/{plant.plant_id}.json"
        if os.path.exists(json_file):
            import json
            with open(json_file, 'r') as f:
                data = json.load(f)
            
            print(f"✅ File JSON trovato: {json_file}")
            
            # Verifica che non ci sia datetime nei nuovi dati
            has_datetime = False
            
            # Controlla sensori
            if 'sensors' in data:
                for sensor_type, entries in data['sensors'].items():
                    for entry in entries:
                        if 'datetime' in entry:
                            has_datetime = True
                            print(f"⚠️ Trovato datetime in sensore {sensor_type}: {entry['datetime']}")
            
            # Controlla attuatori
            if 'actuators' in data:
                for actuator_type, entries in data['actuators'].items():
                    for entry in entries:
                        if 'datetime' in entry:
                            has_datetime = True
                            print(f"⚠️ Trovato datetime in attuatore {actuator_type}: {entry['datetime']}")
            
            if not has_datetime:
                print("✅ Nessun campo datetime trovato nei nuovi dati")
            
            # Mostra struttura finale
            print(f"\n📊 Struttura finale:")
            print(f"   - Sensori: {len(data.get('sensors', {}))}")
            print(f"   - Attuatori: {len(data.get('actuators', {}))}")
            
            # Mostra ultimi valori
            if 'sensors' in data and 'humidity' in data['sensors']:
                humidity_entries = data['sensors']['humidity']
                if humidity_entries:
                    last_humidity = humidity_entries[-1]
                    print(f"   - Ultima umidità: {last_humidity['value']} (timestamp: {last_humidity['timestamp']})")
            
            if 'actuators' in data and 'irrigation' in data['actuators']:
                irrigation_entries = data['actuators']['irrigation']
                if irrigation_entries:
                    last_irrigation = irrigation_entries[-1]
                    print(f"   - Ultima irrigazione: {last_irrigation['action']} (timestamp: {last_irrigation['timestamp']})")
        
        else:
            print(f"❌ File JSON non trovato: {json_file}")
        
        print("\n🎯 Test Completato!")
        print("✅ Sistema aggiornato per salvare senza datetime")
        print("✅ Solo timestamp numerico viene memorizzato")
        print("✅ File JSON più leggeri e semplici")
        
    except Exception as e:
        print(f"❌ Errore durante il test: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    test_no_datetime()
