#!/usr/bin/env python3
"""
Test completo del sistema di salvataggio dati JSON.
"""

import paho.mqtt.publish as publish
import time
import json
import os

def test_json_saving_system():
    """Test completo del sistema di salvataggio JSON."""
    
    print("🧪 Test Sistema Salvataggio JSON")
    print("=" * 50)
    
    # Configurazione MQTT
    BROKER_ADDRESS = "127.0.0.1"
    BROKER_PORT = 7883
    
    # Test data
    test_data = [
        ("plant/sensor/humidity", "65"),
        ("plant/sensor/temperature", "25"),
        ("plant/sensor/lightness", "500"),
        ("plant/sensor/battery_level", "85"),
        ("plant/sensor/humidity", "70"),  # Secondo valore per testare accumulo
    ]
    
    print("📤 Invio dati di test...")
    
    # Invia tutti i dati
    for topic, value in test_data:
        publish.single(topic, value, hostname=BROKER_ADDRESS, port=BROKER_PORT)
        print(f"📤 Inviato: {topic} = {value}")
        time.sleep(1)  # Pausa tra i messaggi
    
    print("\n⏳ Attesa elaborazione...")
    time.sleep(3)
    
    # Verifica file creati
    print("\n📁 Verifica file JSON creati...")
    log_dir = "cloud_simulator/plants_log"
    
    if os.path.exists(log_dir):
        files = [f for f in os.listdir(log_dir) if f.endswith('.json')]
        print(f"   File JSON trovati: {len(files)}")
        
        for file in files:
            file_path = os.path.join(log_dir, file)
            try:
                with open(file_path, 'r') as f:
                    data = json.load(f)
                
                # Verifica struttura
                if isinstance(data, dict) and 'plant_id' in data:
                    print(f"   ✅ {file}: Struttura corretta")
                    if 'sensors' in data:
                        sensor_count = sum(len(sensor_data) for sensor_data in data['sensors'].values())
                        print(f"      - Sensori: {sensor_count} entry")
                    if 'actuators' in data:
                        actuator_count = sum(len(actuator_data) for actuator_data in data['actuators'].values())
                        print(f"      - Attuatori: {actuator_count} entry")
                else:
                    print(f"   ⚠️ {file}: Struttura non standard")
                    
            except Exception as e:
                print(f"   ❌ {file}: Errore lettura - {e}")
    else:
        print("   ❌ Directory non trovata")
    
    print("\n🎯 Test completato!")

if __name__ == "__main__":
    test_json_saving_system()
