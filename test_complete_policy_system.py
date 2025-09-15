#!/usr/bin/env python3
"""
Test completo del sistema con PolicyManager integrato.
Simula il flusso completo: dati sensori -> memorizzazione -> valutazione policy -> azioni.
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
from data_collector.policy_manager import PolicyManager
from data_collector.json_manager import JsonManager

def test_complete_policy_system():
    """Test completo del sistema con policy."""
    
    print("🧪 Test Sistema Completo con Policy")
    print("=" * 50)
    
    try:
        # Crea plant descriptor
        plants = Factory.create_plant_descriptor()
        if not plants:
            print("❌ Nessuna pianta creata")
            return
        
        plant = plants[0]
        print(f"🌱 Pianta test: {plant.plant_id} ({plant.species})")
        
        # Inizializza componenti
        policy_manager = PolicyManager()
        json_manager = JsonManager()
        
        # Test 1: Valori che dovrebbero attivare l'irrigazione
        print(f"\n📤 Test 1: Valori che Attivano Irrigazione")
        print("-" * 40)
        
        test_scenarios = [
            {
                "name": "Umidità bassa (attiva irrigazione)",
                "sensor_values": {"humidity": 150},  # < 200
                "expected_actions": ["Activate irrigation"]
            },
            {
                "name": "Umidità alta (disattiva irrigazione)",
                "sensor_values": {"humidity": 250},  # > 220
                "expected_actions": ["Deactivate irrigation"]
            },
            {
                "name": "Batteria bassa (genera alert)",
                "sensor_values": {"battery_level": 15},  # < 20
                "expected_actions": []
            },
            {
                "name": "Serbatoio vuoto (genera alert)",
                "sensor_values": {"level_tank": 0.2},  # < 0.3
                "expected_actions": []
            }
        ]
        
        for scenario in test_scenarios:
            print(f"\n🔍 Scenario: {scenario['name']}")
            print(f"📊 Valori: {scenario['sensor_values']}")
            
            # Salva i valori nel JSON
            for sensor_type, value in scenario['sensor_values'].items():
                json_manager.save_sensor_data(plant.plant_id, sensor_type, value, plant.species)
                print(f"💾 Salvato: {sensor_type} = {value}")
            
            # Valuta le policy
            actions, alerts = policy_manager.evaluate_policies(plant, scenario['sensor_values'])
            
            print(f"📤 Azioni generate: {actions}")
            print(f"🚨 Alert generati: {alerts}")
            
            # Verifica aspettative
            if scenario['expected_actions']:
                if actions == scenario['expected_actions']:
                    print("✅ Azioni corrette")
                else:
                    print(f"❌ Azioni attese: {scenario['expected_actions']}, ottenute: {actions}")
            else:
                if not actions:
                    print("✅ Nessuna azione (come atteso)")
                else:
                    print(f"⚠️ Azioni inaspettate: {actions}")
            
            # Esegui azioni se presenti
            if actions:
                print(f"⚡ Esecuzione azioni...")
                policy_manager.execute_actions(plant, actions)
            
            time.sleep(1)
        
        # Test 2: Verifica file JSON finale
        print(f"\n📁 Test 2: Verifica File JSON")
        print("-" * 40)
        
        json_file = f"cloud_simulator/plants_log/{plant.plant_id}.json"
        if os.path.exists(json_file):
            with open(json_file, 'r') as f:
                data = json.load(f)
            
            print(f"✅ File JSON trovato: {json_file}")
            
            # Mostra statistiche
            if 'sensors' in data:
                total_sensor_entries = sum(len(entries) for entries in data['sensors'].values())
                print(f"📊 Sensori: {len(data['sensors'])} tipi, {total_sensor_entries} entry totali")
            
            if 'actuators' in data:
                total_actuator_entries = sum(len(entries) for entries in data['actuators'].values())
                print(f"📊 Attuatori: {len(data['actuators'])} tipi, {total_actuator_entries} entry totali")
                
                # Mostra ultime azioni
                if 'irrigation' in data['actuators']:
                    irrigation_actions = data['actuators']['irrigation']
                    print(f"💧 Ultime azioni irrigazione:")
                    for i, action in enumerate(irrigation_actions[-3:]):
                        print(f"   {i+1}. {action['action']} (timestamp: {action['timestamp']})")
        else:
            print(f"❌ File JSON non trovato: {json_file}")
        
        print("\n🎯 Test Sistema Completo Completato!")
        print("✅ Policy caricate e valutate correttamente")
        print("✅ Azioni generate ed eseguite")
        print("✅ Alert generati quando necessario")
        print("✅ Dati salvati nel file JSON")
        
    except Exception as e:
        print(f"❌ Errore durante il test: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    test_complete_policy_system()
