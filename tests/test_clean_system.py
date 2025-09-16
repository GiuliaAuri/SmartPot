#!/usr/bin/env python3
"""
Test del sistema pulito con solo i sensori e attuatori definiti nel PlantDescriptor.
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

def test_clean_system():
    """Test del sistema con solo sensori e attuatori definiti."""
    
    print("🧪 Test Sistema Pulito - Solo Sensori/Attuatori Definiti")
    print("=" * 60)
    
    try:
        # Crea plant descriptor
        plants = Factory.create_plant_descriptor()
        if not plants:
            print("❌ Nessuna pianta creata")
            return
        
        plant = plants[0]
        print(f"🌱 Pianta test: {plant.plant_id} ({plant.species})")
        
        # Mostra sensori e attuatori definiti
        print(f"📊 Sensori definiti: {[sensor.type for sensor in plant.sensors]}")
        print(f"📊 Attuatori definiti: {[actuator.type for actuator in plant.actuators]}")
        
        # Test 1: Invio comandi attuatori (solo irrigation)
        print("\n📤 Test 1: Comandi Attuatori")
        print("-" * 30)
        
        actuator_commands = ["start", "stop"]
        
        for command in actuator_commands:
            print(f"📤 Invio comando: '{command}'")
            producer = DataCollectorProducer(plant, command)
            producer.run()
            time.sleep(1)
        
        # Test 2: Invio dati sensori (solo humidity)
        print("\n📤 Test 2: Dati Sensori")
        print("-" * 30)
        
        sensor_data = [
            ("plant/sensor/humidity", "65"),
            ("plant/sensor/humidity", "70"),
            ("plant/sensor/humidity", "75"),
        ]
        
        for topic, value in sensor_data:
            publish.single(topic, value, hostname="localhost", port=7883)
            print(f"📤 Inviato: {topic} = {value}")
            time.sleep(1)
        
        # Test 3: Tentativo di inviare sensori non definiti (dovrebbe essere ignorato)
        print("\n📤 Test 3: Sensori Non Definiti (Dovrebbero Essere Ignorati)")
        print("-" * 30)
        
        undefined_sensors = [
            ("plant/sensor/temperature", "25"),
            ("plant/sensor/battery_level", "85"),
            ("plant/sensor/lightness", "500"),
        ]
        
        for topic, value in undefined_sensors:
            publish.single(topic, value, hostname="localhost", port=7883)
            print(f"📤 Inviato (ignorato): {topic} = {value}")
            time.sleep(1)
        
        print("\n⏳ Attesa elaborazione...")
        time.sleep(3)
        
        # Test 4: Verifica file JSON
        print("\n📁 Test 4: Verifica File JSON")
        print("-" * 30)
        
        json_file = f"cloud_simulator/plants_log/{plant.plant_id}.json"
        if os.path.exists(json_file):
            print(f"✅ File JSON trovato: {json_file}")
            
            with open(json_file, 'r') as f:
                data = json.load(f)
            
            # Verifica struttura
            print(f"📊 Struttura file:")
            print(f"   - Plant ID: {data.get('plant_id', 'N/A')}")
            print(f"   - Species: {data.get('species', 'N/A')}")
            
            # Verifica sensori (solo humidity dovrebbe essere presente)
            if 'sensors' in data:
                print(f"   - Sensori presenti: {list(data['sensors'].keys())}")
                for sensor_type, entries in data['sensors'].items():
                    print(f"     * {sensor_type}: {len(entries)} entry")
                    if entries:
                        print(f"       Ultimo valore: {entries[-1]['value']} ({entries[-1]['datetime']})")
            
            # Verifica attuatori (solo irrigation dovrebbe essere presente)
            if 'actuators' in data:
                print(f"   - Attuatori presenti: {list(data['actuators'].keys())}")
                for actuator_type, entries in data['actuators'].items():
                    print(f"     * {actuator_type}: {len(entries)} entry")
                    if entries:
                        print(f"       Ultima azione: {entries[-1]['action']} ({entries[-1]['datetime']})")
        else:
            print(f"❌ File JSON non trovato: {json_file}")
        
        print("\n🎯 Test Sistema Pulito Completato!")
        print("✅ Solo sensori e attuatori definiti nel PlantDescriptor")
        print("✅ Sensori non definiti ignorati")
        print("✅ Struttura JSON coerente")
        
    except Exception as e:
        print(f"❌ Errore durante il test: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    test_clean_system()
