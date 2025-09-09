#!/usr/bin/env python3
"""
Test per verificare che i dati delle piante siano diversi per ogni pianta.
"""

import json
import os
import sys

# Aggiungi il path del progetto
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from managers.plant_data_manager import PlantDataManager

def test_plant_data_differences():
    """
    Testa che i dati delle piante siano diversi per ogni pianta.
    """
    print("🧪 Test: Verifica differenze nei dati delle piante")
    
    # Crea il manager
    data_manager = PlantDataManager()
    
    # Carica le configurazioni
    if not data_manager.load_configurations():
        print("   ❌ FAIL: Impossibile caricare le configurazioni")
        return False
    
    # Carica i dati delle piante
    plants_data = data_manager.load_plants_data()
    
    if not plants_data:
        print("   ❌ FAIL: Nessun dato delle piante caricato")
        return False
    
    print(f"   📊 Caricate {len(plants_data)} piante")
    
    # Verifica che ogni pianta abbia dati diversi
    plant_ids = list(plants_data.keys())
    
    for i, plant_id in enumerate(plant_ids):
        plant_data = plants_data[plant_id]
        sensors = plant_data.get('sensors', [])
        
        print(f"   🌱 {plant_id}:")
        
        # Estrai alcuni valori chiave
        temperature_values = []
        humidity_values = []
        battery_values = []
        
        for sensor in sensors:
            if isinstance(sensor, dict):
                sensor_name = sensor.get('sensor')
                values = sensor.get('values', [])
                if values:
                    latest_value = values[-1].get('value', 0)
                    
                    if sensor_name == 'temperature':
                        temperature_values.append(latest_value)
                    elif sensor_name == 'humidity':
                        humidity_values.append(latest_value)
                    elif sensor_name == 'battery_level':
                        battery_values.append(latest_value)
        
        # Mostra i valori
        if temperature_values:
            print(f"      🌡️  Temperatura: {temperature_values[-1]:.1f}°C")
        if humidity_values:
            print(f"      💧 Umidità: {humidity_values[-1]:.1f}%")
        if battery_values:
            print(f"      🔋 Batteria: {battery_values[-1]:.1f}%")
    
    # Verifica che ci siano differenze
    all_temperatures = []
    all_humidities = []
    all_batteries = []
    
    for plant_id, plant_data in plants_data.items():
        sensors = plant_data.get('sensors', [])
        
        for sensor in sensors:
            if isinstance(sensor, dict):
                sensor_name = sensor.get('sensor')
                values = sensor.get('values', [])
                if values:
                    latest_value = values[-1].get('value', 0)
                    
                    if sensor_name == 'temperature':
                        all_temperatures.append(latest_value)
                    elif sensor_name == 'humidity':
                        all_humidities.append(latest_value)
                    elif sensor_name == 'battery_level':
                        all_batteries.append(latest_value)
    
    # Controlla se ci sono differenze
    temp_unique = len(set(all_temperatures)) > 1
    hum_unique = len(set(all_humidities)) > 1
    bat_unique = len(set(all_batteries)) > 1
    
    print(f"\n   📈 Analisi differenze:")
    print(f"      🌡️  Temperature diverse: {temp_unique} ({len(set(all_temperatures))} valori unici)")
    print(f"      💧 Umidità diverse: {hum_unique} ({len(set(all_humidities))} valori unici)")
    print(f"      🔋 Batterie diverse: {bat_unique} ({len(set(all_batteries))} valori unici)")
    
    if temp_unique or hum_unique or bat_unique:
        print("   ✅ PASS: I dati delle piante sono diversi")
        return True
    else:
        print("   ❌ FAIL: Tutti i dati delle piante sono identici")
        return False

def main():
    """
    Esegue il test di verifica dei dati delle piante.
    """
    print("🚀 Test Verifica Dati Piante")
    print("=" * 50)
    
    try:
        success = test_plant_data_differences()
        
        print("\n" + "=" * 50)
        if success:
            print("🎉 Test completato con successo!")
        else:
            print("⚠️  Test fallito - i dati potrebbero essere identici")
        
        return success
        
    except Exception as e:
        print(f"❌ Errore durante il test: {e}")
        return False

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
