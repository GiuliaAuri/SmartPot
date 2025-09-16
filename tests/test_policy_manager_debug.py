#!/usr/bin/env python3
"""
Test per verificare il PolicyManager e capire perché restituisce 
alert e azioni invertiti
"""

import sys
import os

# Aggiungi il path per importare i moduli del progetto
project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), '.'))
sys.path.insert(0, project_root)

from data_collector.factory.factory import Factory
from data_collector.policy_manager import PolicyManager

def test_policy_manager_debug():
    """Test per debuggare il PolicyManager."""
    
    print("🧪 Test Debug PolicyManager")
    print("=" * 40)
    
    try:
        # Crea plant descriptor
        plants = Factory.create_plant_descriptor()
        if not plants:
            print("❌ Nessuna pianta creata")
            return
        
        plant = plants[0]
        print(f"🌱 Pianta test: {plant.plant_id} ({plant.species})")
        
        # Crea PolicyManager
        policy_manager = PolicyManager()
        
        # Verifica le policy caricate
        policies = policy_manager.get_policies_for_plant(plant.plant_id)
        print(f"\n📊 Policy caricate per {plant.plant_id}: {len(policies)}")
        for i, policy in enumerate(policies):
            print(f"   {i+1}. {policy['sensor']} {policy['condition']} {policy['value']} -> {policy['action']}")
        
        # Test con valori che dovrebbero attivare diverse policy
        print(f"\n🔍 Test Valutazione Policy")
        print("-" * 30)
        
        # Scenario 1: Umidità bassa + batteria bassa + serbatoio vuoto
        sensor_values_1 = {
            "humidity": 150,      # < 200 -> attiva irrigazione
            "battery_level": 15,  # < 20 -> alert
            "level_tank": 0.2     # < 0.3 -> alert
        }
        
        print(f"📊 Scenario 1: {sensor_values_1}")
        actions_1, alerts_1 = policy_manager.evaluate_policies(plant, sensor_values_1)
        print(f"📤 Azioni: {actions_1}")
        print(f"🚨 Alert: {alerts_1}")
        
        # Scenario 2: Solo umidità alta
        sensor_values_2 = {
            "humidity": 250       # > 220 -> disattiva irrigazione
        }
        
        print(f"\n📊 Scenario 2: {sensor_values_2}")
        actions_2, alerts_2 = policy_manager.evaluate_policies(plant, sensor_values_2)
        print(f"📤 Azioni: {actions_2}")
        print(f"🚨 Alert: {alerts_2}")
        
        # Scenario 3: Solo batteria bassa
        sensor_values_3 = {
            "battery_level": 15   # < 20 -> alert
        }
        
        print(f"\n📊 Scenario 3: {sensor_values_3}")
        actions_3, alerts_3 = policy_manager.evaluate_policies(plant, sensor_values_3)
        print(f"📤 Azioni: {actions_3}")
        print(f"🚨 Alert: {alerts_3}")
        
    except Exception as e:
        print(f"❌ Errore durante il test: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    test_policy_manager_debug()
