#!/usr/bin/env python3
"""
Test per verificare che la scrittura sicura dei file JSON funzioni correttamente.
"""

import json
import os
import sys
import time
import tempfile
import shutil

# Aggiungi il path del progetto
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from plants_system.process.data_collector_consumer import DataCollectorConsumer
from plants_system.smart_objects.models.plant_descriptor import PlantDescriptor
from plants_system.smart_objects.models.Device import Device
from plants_system.smart_objects.sensors.temperature_sensor import TemperatureSensor
from plants_system.smart_objects.sensors.humidity_sensor import HumiditySensor
from plants_system.smart_objects.actuators.irrigation_actuator import IrrigationActuator

def test_safe_json_writing():
    """
    Testa che la scrittura sicura dei file JSON funzioni correttamente.
    """
    print("🧪 Test: Verifica scrittura sicura dei file JSON")
    
    # Crea una directory temporanea per i test
    test_dir = tempfile.mkdtemp()
    test_file = os.path.join(test_dir, "test_plant.json")
    
    try:
        # Crea un plant descriptor di test
        sensor1 = TemperatureSensor("test_plant", 25.0, "°C", -10.0, 50.0, "environment_telemetry")
        sensor2 = HumiditySensor("test_plant", 60.0, "%", 0.0, 100.0, "environment_telemetry")
        actuator1 = IrrigationActuator("test_plant")
        
        device = Device("test_plant", "environment_telemetry", [sensor1, sensor2], [actuator1])
        plant_descriptor = PlantDescriptor("Test Plant", "test_plant")
        
        # Crea il consumer
        consumer = DataCollectorConsumer(plant_descriptor, test_dir + "/")
        
        print("   📝 Testando scrittura sensori...")
        
        # Test scrittura sensori
        consumer.update_sensor_history("temperature", 25.5, "environment_telemetry")
        consumer.update_sensor_history("humidity", 65.0, "environment_telemetry")
        consumer.update_sensor_history("temperature", 26.0, "environment_telemetry")  # Valore diverso
        
        # Verifica che il file sia stato creato correttamente
        if os.path.exists(test_file):
            with open(test_file, "r") as f:
                data = json.load(f)
            
            if isinstance(data, list) and len(data) > 0:
                plant_data = data[0]
                sensors = plant_data.get("sensors", [])
                
                print(f"      ✅ File creato correttamente con {len(sensors)} sensori")
                
                # Verifica che i sensori abbiano i valori corretti
                temp_sensor = next((s for s in sensors if s.get("sensor") == "temperature"), None)
                hum_sensor = next((s for s in sensors if s.get("sensor") == "humidity"), None)
                
                if temp_sensor and len(temp_sensor.get("values", [])) == 2:
                    print(f"      ✅ Sensore temperatura: {len(temp_sensor['values'])} valori")
                else:
                    print(f"      ❌ Sensore temperatura: dati mancanti")
                    return False
                
                if hum_sensor and len(hum_sensor.get("values", [])) == 1:
                    print(f"      ✅ Sensore umidità: {len(hum_sensor['values'])} valori")
                else:
                    print(f"      ❌ Sensore umidità: dati mancanti")
                    return False
            else:
                print(f"      ❌ Struttura dati non valida")
                return False
        else:
            print(f"      ❌ File non creato")
            return False
        
        print("   📝 Testando scrittura attuatori...")
        
        # Test scrittura attuatori
        consumer.update_actuator_history("Activate irrigation")
        consumer.update_actuator_history("Deactivate irrigation")
        
        # Verifica che gli attuatori siano stati aggiunti
        with open(test_file, "r") as f:
            data = json.load(f)
        
        plant_data = data[0]
        actuators = plant_data.get("actuators", [])
        
        irrigation_actuator = next((a for a in actuators if a.get("actuator") == "irrigation"), None)
        
        if irrigation_actuator and len(irrigation_actuator.get("values", [])) == 2:
            print(f"      ✅ Attuatore irrigazione: {len(irrigation_actuator['values'])} valori")
        else:
            print(f"      ❌ Attuatore irrigazione: dati mancanti")
            return False
        
        print("   📝 Testando scrittura alert...")
        
        # Test scrittura alert
        consumer.update_alerts_history(["Test alert message"])
        consumer.update_alerts_history(["Another alert message"])
        
        # Verifica che gli alert siano stati aggiunti
        with open(test_file, "r") as f:
            data = json.load(f)
        
        plant_data = data[0]
        alerts = plant_data.get("alerts", [])
        
        if len(alerts) == 2:
            print(f"      ✅ Alert: {len(alerts)} messaggi salvati")
        else:
            print(f"      ❌ Alert: {len(alerts)} messaggi (attesi 2)")
            return False
        
        print("   📝 Testando gestione errori...")
        
        # Test gestione errori - prova a scrivere in un file di sola lettura
        read_only_file = os.path.join(test_dir, "read_only.json")
        with open(read_only_file, "w") as f:
            json.dump([], f)
        
        # Rendi il file di sola lettura (su Windows)
        try:
            os.chmod(read_only_file, 0o444)
            
            # Prova a scrivere nel file di sola lettura
            consumer.filename = read_only_file
            result = consumer._safe_write_json([{"test": "data"}])
            
            if not result:
                print(f"      ✅ Gestione errori: scrittura fallita correttamente")
            else:
                print(f"      ❌ Gestione errori: scrittura dovrebbe essere fallita")
                return False
                
        except Exception as e:
            print(f"      ⚠️  Gestione errori: {e} (normale su Windows)")
        
        print("   ✅ PASS: Scrittura sicura dei file JSON funziona correttamente")
        return True
        
    except Exception as e:
        print(f"   ❌ FAIL: Errore durante il test: {e}")
        return False
        
    finally:
        # Pulisci la directory temporanea
        try:
            shutil.rmtree(test_dir)
        except Exception:
            pass

def main():
    """
    Esegue il test di scrittura sicura dei file JSON.
    """
    print("🚀 Test Scrittura Sicura File JSON")
    print("=" * 50)
    
    try:
        success = test_safe_json_writing()
        
        print("\n" + "=" * 50)
        if success:
            print("🎉 Test completato con successo!")
        else:
            print("⚠️  Test fallito")
        
        return success
        
    except Exception as e:
        print(f"❌ Errore durante il test: {e}")
        return False

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
