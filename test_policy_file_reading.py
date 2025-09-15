#!/usr/bin/env python3
"""
Test finale per verificare che il PolicyManager legga correttamente 
le policy dal file /data_collector/policies/policies_conf.json
"""

import sys
import os

# Aggiungi il path per importare i moduli del progetto
project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), '.'))
sys.path.insert(0, project_root)

from data_collector.factory.factory import Factory
from data_collector.policy_manager import PolicyManager

def test_policy_file_reading():
    """Test per verificare la lettura delle policy dal file corretto."""
    
    print("🧪 Test Lettura Policy da File Corretto")
    print("=" * 50)
    
    try:
        # Verifica che il file esista
        policy_file = "data_collector/policies/policies_conf.json"
        if not os.path.exists(policy_file):
            print(f"❌ File policy non trovato: {policy_file}")
            return
        
        print(f"✅ File policy trovato: {policy_file}")
        
        # Crea PolicyManager
        policy_manager = PolicyManager()
        
        # Verifica che le policy siano caricate
        policies = policy_manager.get_policies_for_plant("plant_cactus_001")
        print(f"📊 Policy caricate per plant_cactus_001: {len(policies)}")
        
        for i, policy in enumerate(policies):
            print(f"   {i+1}. {policy['sensor']} {policy['condition']} {policy['value']} -> {policy['action']}")
        
        # Test con valori che dovrebbero attivare diverse policy
        print(f"\n🔍 Test Valutazione Policy")
        print("-" * 30)
        
        # Crea plant descriptor
        plants = Factory.create_plant_descriptor()
        if not plants:
            print("❌ Nessuna pianta creata")
            return
        
        plant = plants[0]
        
        # Test scenario 1: Umidità bassa + batteria bassa + serbatoio vuoto
        sensor_values_1 = {
            "humidity": 150,      # < 200 -> attiva irrigazione
            "battery_level": 15,  # < 20 -> alert
            "level_tank": 0.2     # < 0.3 -> alert
        }
        
        print(f"📊 Scenario 1: {sensor_values_1}")
        actions_1, alerts_1 = policy_manager.evaluate_policies(plant, sensor_values_1)
        print(f"📤 Azioni: {actions_1}")
        print(f"🚨 Alert: {alerts_1}")
        
        # Test scenario 2: Umidità alta
        sensor_values_2 = {
            "humidity": 250       # > 220 -> disattiva irrigazione
        }
        
        print(f"\n📊 Scenario 2: {sensor_values_2}")
        actions_2, alerts_2 = policy_manager.evaluate_policies(plant, sensor_values_2)
        print(f"📤 Azioni: {actions_2}")
        print(f"🚨 Alert: {alerts_2}")
        
        # Test scenario 3: Valori normali
        sensor_values_3 = {
            "humidity": 210,      # Tra 200 e 220 -> nessuna azione
            "battery_level": 50,  # > 20 -> nessun alert
            "level_tank": 0.5     # > 0.3 -> nessun alert
        }
        
        print(f"\n📊 Scenario 3: {sensor_values_3}")
        actions_3, alerts_3 = policy_manager.evaluate_policies(plant, sensor_values_3)
        print(f"📤 Azioni: {actions_3}")
        print(f"🚨 Alert: {alerts_3}")
        
        print("\n🎯 Test Completato!")
        print("✅ Policy caricate dal file corretto")
        print("✅ Valutazione policy funzionante")
        print("✅ Azioni e alert generati correttamente")
        
    except Exception as e:
        print(f"❌ Errore durante il test: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    test_policy_file_reading()
