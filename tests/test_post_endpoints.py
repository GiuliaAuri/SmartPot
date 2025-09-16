#!/usr/bin/env python3
"""
Test script per verificare gli endpoint POST del web server.
"""

import requests
import json
import time

API_BASE_URL = "http://localhost:5000/api"

def test_post_endpoints():
    """Testa gli endpoint POST per il controllo degli attuatori."""
    
    print("🧪 Test Endpoint POST - Controllo Attuatori")
    print("=" * 50)
    
    plant_id = "plant_cactus_001"
    
    try:
        # Test 1: Attiva irrigazione usando endpoint generico
        print("1. Test Attiva Irrigazione (Endpoint Generico)...")
        response = requests.post(
            f"{API_BASE_URL}/plants/{plant_id}/actuators/irrigation",
            json={"action": "start"},
            headers={"Content-Type": "application/json"}
        )
        
        if response.status_code == 200:
            data = response.json()
            print(f"   ✅ Irrigazione attivata: {data['message']}")
            print(f"   📤 MQTT inviato: {data['mqtt_sent']}")
        else:
            print(f"   ❌ Errore: {response.status_code} - {response.text}")
        
        print()
        
        # Test 2: Disattiva irrigazione usando endpoint generico
        print("2. Test Disattiva Irrigazione (Endpoint Generico)...")
        response = requests.post(
            f"{API_BASE_URL}/plants/{plant_id}/actuators/irrigation",
            json={"action": "stop"},
            headers={"Content-Type": "application/json"}
        )
        
        if response.status_code == 200:
            data = response.json()
            print(f"   ✅ Irrigazione disattivata: {data['message']}")
            print(f"   📤 MQTT inviato: {data['mqtt_sent']}")
        else:
            print(f"   ❌ Errore: {response.status_code} - {response.text}")
        
        print()
        
        # Test 3: Test con altri tipi di attuatore (esempio)
        print("3. Test Altri Attuatori (Esempio)...")
        response = requests.post(
            f"{API_BASE_URL}/plants/{plant_id}/actuators/lighting",
            json={"action": "activate"},
            headers={"Content-Type": "application/json"}
        )
        
        if response.status_code == 200:
            data = response.json()
            print(f"   ✅ Attuatore controllato: {data['message']}")
            print(f"   📤 MQTT inviato: {data['mqtt_sent']}")
        else:
            print(f"   ❌ Errore: {response.status_code} - {response.text}")
        
        print()
        
        # Test 4: Verifica dati salvati
        print("4. Verifica Dati Salvati...")
        response = requests.get(f"{API_BASE_URL}/plants/{plant_id}")
        
        if response.status_code == 200:
            plant_data = response.json()
            actuators = plant_data.get('actuators', {})
            print(f"   📊 Attuatori nel file: {list(actuators.keys())}")
            
            if 'irrigation' in actuators:
                irrigation_data = actuators['irrigation']
                print(f"   💧 Azioni irrigazione: {len(irrigation_data)}")
                if irrigation_data:
                    latest = irrigation_data[-1]
                    action = latest.get('action', 'N/A')
                    timestamp = latest.get('timestamp', 'N/A')
                    print(f"   Ultima azione: {action} (timestamp: {timestamp})")
        else:
            print(f"   ❌ Errore nel recupero dati: {response.status_code}")
        
        print()
        print("🎉 Tutti i test POST completati!")
        
    except requests.exceptions.ConnectionError:
        print("❌ Errore di connessione!")
        print("   Assicurati che il server web_api_server.py sia in esecuzione su porta 5000")
    except Exception as e:
        print(f"❌ Errore durante i test: {e}")

if __name__ == "__main__":
    test_post_endpoints()
