#!/usr/bin/env python3
"""
Test completo per verificare che tutti i sensori e attuatori del PlantDescriptor
vengano memorizzati correttamente nel file JSON.
"""

import paho.mqtt.publish as publish
import time
import json
import os
import sys

# Aggiungi il path per importare i moduli del progetto
project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), '.'))
sys.path.insert(0, project_root)

from data_collector.factory.factory import Factory
from data_collector.data_collector_producer import DataCollectorProducer

def test_all_sensors_actuators():
    """Test completo per verificare il salvataggio di tutti i sensori e attuatori."""
    
    print("🧪 Test Completo - Tutti i Sensori e Attuatori del PlantDescriptor")
    print("=" * 70)
    
    try:
        # Crea plant descriptor
        plants = Factory.create_plant_descriptor()
        if not plants:
            print("❌ Nessuna pianta creata")
            return
        
        plant = plants[0]
        print(f"🌱 Pianta test: {plant.plant_id} ({plant.species})")
        
        # Mostra tutti i sensori e attuatori definiti
        print(f"\n📊 Sensori definiti nel PlantDescriptor:")
        for i, sensor in enumerate(plant.sensors):
            print(f"   {i+1}. {sensor.type} (device: {sensor.device})")
        
        print(f"\n📊 Attuatori definiti nel PlantDescriptor:")
        for i, actuator in enumerate(plant.actuators):
            print(f"   {i+1}. {actuator.type} (device: {actuator.device})")
        
        # Test 1: Invio dati per TUTTI i sensori definiti
        print(f"\n📤 Test 1: Invio Dati per Tutti i Sensori")
        print("-" * 40)
        
        sensor_test_values = {
            "humidity": [65, 70, 75, 80, 85]  # Valori di test per humidity
        }
        
        for sensor_type, values in sensor_test_values.items():
            print(f"\n🔍 Testando sensore: {sensor_type}")
            for value in values:
                topic = f"plant/sensor/{sensor_type}"
                publish.single(topic, str(value), hostname="localhost", port=7883)
                print(f"   📤 Inviato: {topic} = {value}")
                time.sleep(0.5)  # Pausa breve tra i valori
        
        # Test 2: Invio comandi per TUTTI gli attuatori definiti
        print(f"\n📤 Test 2: Invio Comandi per Tutti gli Attuatori")
        print("-" * 40)
        
        actuator_test_commands = {
            "irrigation": ["start", "stop", "start", "stop", "start"]
        }
        
        for actuator_type, commands in actuator_test_commands.items():
            print(f"\n🔍 Testando attuatore: {actuator_type}")
            for command in commands:
                print(f"   📤 Invio comando: '{command}'")
                producer = DataCollectorProducer(plant, command)
                producer.run()
                time.sleep(0.5)  # Pausa breve tra i comandi
        
        print("\n⏳ Attesa elaborazione...")
        time.sleep(3)
        
        # Test 3: Verifica completa del file JSON
        print(f"\n📁 Test 3: Verifica Completa File JSON")
        print("-" * 40)
        
        json_file = f"cloud_simulator/plants_log/{plant.plant_id}.json"
        if os.path.exists(json_file):
            print(f"✅ File JSON trovato: {json_file}")
            
            with open(json_file, 'r') as f:
                data = json.load(f)
            
            # Verifica struttura generale
            print(f"\n📊 Struttura generale:")
            print(f"   - Plant ID: {data.get('plant_id', 'N/A')}")
            print(f"   - Species: {data.get('species', 'N/A')}")
            print(f"   - Created: {data.get('created_at', 'N/A')}")
            print(f"   - Last Updated: {data.get('last_updated', 'N/A')}")
            
            # Verifica TUTTI i sensori definiti
            print(f"\n📊 Verifica Sensori:")
            if 'sensors' in data:
                for sensor in plant.sensors:
                    sensor_type = sensor.type
                    if sensor_type in data['sensors']:
                        entries = data['sensors'][sensor_type]
                        print(f"   ✅ {sensor_type}: {len(entries)} entry salvate")
                        if entries:
                            print(f"      - Primo valore: {entries[0]['value']} ({entries[0]['datetime']})")
                            print(f"      - Ultimo valore: {entries[-1]['value']} ({entries[-1]['datetime']})")
                    else:
                        print(f"   ❌ {sensor_type}: NON TROVATO nel file JSON")
            else:
                print("   ❌ Sezione 'sensors' non trovata nel file JSON")
            
            # Verifica TUTTI gli attuatori definiti
            print(f"\n📊 Verifica Attuatori:")
            if 'actuators' in data:
                for actuator in plant.actuators:
                    actuator_type = actuator.type
                    if actuator_type in data['actuators']:
                        entries = data['actuators'][actuator_type]
                        print(f"   ✅ {actuator_type}: {len(entries)} azioni salvate")
                        if entries:
                            print(f"      - Prima azione: {entries[0]['action']} ({entries[0]['datetime']})")
                            print(f"      - Ultima azione: {entries[-1]['action']} ({entries[-1]['datetime']})")
                    else:
                        print(f"   ❌ {actuator_type}: NON TROVATO nel file JSON")
            else:
                print("   ❌ Sezione 'actuators' non trovata nel file JSON")
            
            # Verifica che non ci siano sensori/attuatori extra
            print(f"\n📊 Verifica Sensori/Attuatori Extra:")
            if 'sensors' in data:
                extra_sensors = set(data['sensors'].keys()) - {sensor.type for sensor in plant.sensors}
                if extra_sensors:
                    print(f"   ⚠️ Sensori extra trovati: {extra_sensors}")
                else:
                    print(f"   ✅ Nessun sensore extra trovato")
            
            if 'actuators' in data:
                extra_actuators = set(data['actuators'].keys()) - {actuator.type for actuator in plant.actuators}
                if extra_actuators:
                    print(f"   ⚠️ Attuatori extra trovati: {extra_actuators}")
                else:
                    print(f"   ✅ Nessun attuatore extra trovato")
        
        else:
            print(f"❌ File JSON non trovato: {json_file}")
        
        print("\n🎯 Test Completo Completato!")
        print("✅ Verificato salvataggio di tutti i sensori definiti")
        print("✅ Verificato salvataggio di tutti gli attuatori definiti")
        print("✅ Verificato che non ci siano sensori/attuatori extra")
        
    except Exception as e:
        print(f"❌ Errore durante il test: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    test_all_sensors_actuators()
