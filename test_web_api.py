#!/usr/bin/env python3
"""
Test script per verificare l'API REST del web server.
"""

import requests
import json
import time

API_BASE_URL = "http://localhost:5000/api"

def test_api_endpoints():
    """Testa tutti gli endpoint dell'API."""
    
    print("🧪 Test API REST Endpoints")
    print("=" * 40)
    
    try:
        # Test health check
        print("1. Test Health Check...")
        response = requests.get(f"{API_BASE_URL}/health")
        if response.status_code == 200:
            health_data = response.json()
            print(f"   ✅ Server healthy: {health_data['status']}")
            print(f"   📊 Piante trovate: {health_data['plants_count']}")
        else:
            print(f"   ❌ Health check failed: {response.status_code}")
        
        print()
        
        # Test get all plants
        print("2. Test Get All Plants...")
        response = requests.get(f"{API_BASE_URL}/plants")
        if response.status_code == 200:
            plants_data = response.json()
            print(f"   ✅ Trovate {len(plants_data)} piante:")
            for plant in plants_data:
                print(f"      📱 {plant['name']}: Umidità {plant['soilMoisture']}%, Irrigazione {'Attiva' if plant['isWatering'] else 'Inattiva'}")
        else:
            print(f"   ❌ Get plants failed: {response.status_code}")
        
        print()
        
        # Test get stats
        print("3. Test Get Stats...")
        response = requests.get(f"{API_BASE_URL}/stats")
        if response.status_code == 200:
            stats_data = response.json()
            print(f"   ✅ Statistiche:")
            print(f"      📊 Piante totali: {stats_data['total_plants']}")
            print(f"      💧 Irrigazioni attive: {stats_data['active_irrigation']}")
            print(f"      📈 Umidità media: {stats_data['avg_soil_moisture']:.1f}%")
        else:
            print(f"   ❌ Get stats failed: {response.status_code}")
        
        print()
        
        # Test get specific plant
        print("4. Test Get Specific Plant...")
        response = requests.get(f"{API_BASE_URL}/plants/plant_cactus_001")
        if response.status_code == 200:
            plant_data = response.json()
            print(f"   ✅ Pianta specifica trovata: {plant_data['name']}")
            print(f"      💧 Umidità: {plant_data['soilMoisture']}%")
            print(f"      🔄 Irrigazione: {'Attiva' if plant_data['isWatering'] else 'Inattiva'}")
        else:
            print(f"   ❌ Get specific plant failed: {response.status_code}")
        
        print()
        print("🎉 Tutti i test completati!")
        
    except requests.exceptions.ConnectionError:
        print("❌ Errore di connessione!")
        print("   Assicurati che il server web_api_server.py sia in esecuzione su porta 5000")
    except Exception as e:
        print(f"❌ Errore durante i test: {e}")

if __name__ == "__main__":
    test_api_endpoints()
