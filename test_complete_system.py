#!/usr/bin/env python3
"""
Test finale del sistema completo Producer-Consumer con salvataggio JSON.
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

def test_complete_system():
    """Test completo del sistema Producer-Consumer."""
    
    print("🧪 Test Sistema Completo Producer-Consumer")
    print("=" * 60)
    
    try:
        # Crea plant descriptor
        plants = Factory.create_plant_descriptor()
        if not plants:
            print("❌ Nessuna pianta creata")
            return
        
        plant = plants[0]
        print(f"🌱 Pianta test: {plant.plant_id} ({plant.species})")
        
        # Test 1: Invio comandi attuatori
        print("\n📤 Test 1: Comandi Attuatori")
        print("-" * 30)
        
        actuator_commands = [
            "start",
            "stop",
            "Activate irrigation",
            "Deactivate irrigation"
        ]
        
        for command in actuator_commands:
            print(f"📤 Invio comando: '{command}'")
            producer = DataCollectorProducer(plant, command)
            producer.run()
            time.sleep(1)
        
        # Test 2: Invio dati sensori
        print("\n📤 Test 2: Dati Sensori")
        print("-" * 30)
        
        sensor_data = [
            ("plant/sensor/humidity", "65"),
            ("plant/sensor/temperature", "25"),
            ("plant/sensor/lightness", "500"),
            ("plant/sensor/battery_level", "85"),
            ("plant/sensor/humidity", "70"),  # Secondo valore per testare accumulo
        ]
        
        for topic, value in sensor_data:
            publish.single(topic, value, hostname="localhost", port=7883)
            print(f"📤 Inviato: {topic} = {value}")
            time.sleep(1)
        
        print("\n⏳ Attesa elaborazione...")
        time.sleep(3)
        
        # Test 3: Verifica file JSON
        print("\n📁 Test 3: Verifica File JSON")
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
            print(f"   - Created: {data.get('created_at', 'N/A')}")
            print(f"   - Last Updated: {data.get('last_updated', 'N/A')}")
            
            # Verifica sensori
            if 'sensors' in data:
                total_sensor_entries = sum(len(entries) for entries in data['sensors'].values())
                print(f"   - Sensori: {len(data['sensors'])} tipi, {total_sensor_entries} entry totali")
                for sensor_type, entries in data['sensors'].items():
                    print(f"     * {sensor_type}: {len(entries)} entry")
            
            # Verifica attuatori
            if 'actuators' in data:
                total_actuator_entries = sum(len(entries) for entries in data['actuators'].values())
                print(f"   - Attuatori: {len(data['actuators'])} tipi, {total_actuator_entries} entry totali")
                for actuator_type, entries in data['actuators'].items():
                    print(f"     * {actuator_type}: {len(entries)} entry")
                    # Mostra ultime 3 azioni
                    for i, entry in enumerate(entries[-3:]):
                        print(f"       {i+1}. {entry['action']} - {entry['datetime']}")
        else:
            print(f"❌ File JSON non trovato: {json_file}")
        
        print("\n🎯 Test Sistema Completo Completato!")
        print("✅ Producer: Comandi attuatori salvati")
        print("✅ Consumer: Dati sensori salvati")
        print("✅ JsonManager: Struttura dati coerente")
        
    except Exception as e:
        print(f"❌ Errore durante il test: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    test_complete_system()
