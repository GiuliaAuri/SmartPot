#!/usr/bin/env python3
"""
Test per verificare l'ottimizzazione delle performance del DataCollectorConsumer.

Questo script testa che il callback on_message sia veloce e non causi
warning di performance MQTT.
"""

import time
import json
import threading
from unittest.mock import MagicMock, patch
import sys
import os

# Aggiungi il path del progetto
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from plants_system.smart_objects.models.plant_descriptor import PlantDescriptor
from plants_system.process.data_collector_consumer import DataCollectorConsumer

def test_on_message_performance():
    """
    Testa che il callback on_message sia veloce (< 10ms).
    """
    print("🧪 Test: Performance del callback on_message")
    
    # Crea un PlantDescriptor mock
    plant_descriptor = MagicMock()
    plant_descriptor.plant_id = "test_plant"
    plant_descriptor.devices = []
    
    # Crea il consumer
    consumer = DataCollectorConsumer(plant_descriptor, "test_path/")
    
    # Mock del messaggio MQTT
    mock_msg = MagicMock()
    mock_msg.topic = "plant/test_plant/device/sensor/telemetry/humidity"
    mock_msg.payload = json.dumps({
        "plant_id": "test_plant",
        "type": "humidity",
        "value": 45.5,
        "device": "environment_telemetry",
        "timestamp": int(time.time())
    }).encode('utf-8')
    
    # Testa la performance del callback
    start_time = time.time()
    
    # Simula 100 chiamate al callback
    for i in range(100):
        consumer.on_message(None, None, mock_msg)
    
    end_time = time.time()
    total_time = (end_time - start_time) * 1000  # Converti in millisecondi
    avg_time = total_time / 100
    
    print(f"   ⏱️  Tempo totale per 100 messaggi: {total_time:.2f}ms")
    print(f"   ⏱️  Tempo medio per messaggio: {avg_time:.2f}ms")
    
    # Verifica che sia veloce (< 10ms per messaggio)
    if avg_time < 10:
        print("   ✅ PASS: Callback on_message è veloce")
        return True
    else:
        print("   ❌ FAIL: Callback on_message è troppo lento")
        return False

def test_message_queue_functionality():
    """
    Testa che la queue dei messaggi funzioni correttamente.
    """
    print("\n🧪 Test: Funzionalità della message queue")
    
    # Crea un PlantDescriptor mock
    plant_descriptor = MagicMock()
    plant_descriptor.plant_id = "test_plant"
    plant_descriptor.devices = []
    
    # Crea il consumer
    consumer = DataCollectorConsumer(plant_descriptor, "test_path/")
    
    # Verifica che la queue sia vuota inizialmente
    if consumer.message_queue.empty():
        print("   ✅ PASS: Queue inizialmente vuota")
    else:
        print("   ❌ FAIL: Queue non vuota all'inizio")
        return False
    
    # Aggiungi un messaggio alla queue
    test_message = {
        'topic': 'test/topic',
        'payload': '{"test": "data"}',
        'sensor_type': 'humidity',
        'value': 50.0,
        'device_name': 'test_device',
        'timestamp': int(time.time())
    }
    
    consumer.message_queue.put(test_message)
    
    # Verifica che il messaggio sia nella queue
    if not consumer.message_queue.empty():
        print("   ✅ PASS: Messaggio aggiunto alla queue")
    else:
        print("   ❌ FAIL: Messaggio non aggiunto alla queue")
        return False
    
    # Verifica che il messaggio sia quello giusto
    retrieved_message = consumer.message_queue.get()
    if retrieved_message == test_message:
        print("   ✅ PASS: Messaggio recuperato correttamente")
        return True
    else:
        print("   ❌ FAIL: Messaggio recuperato non corretto")
        return False

def test_thread_safety():
    """
    Testa che il thread di elaborazione sia thread-safe.
    """
    print("\n🧪 Test: Thread safety")
    
    # Crea un PlantDescriptor mock
    plant_descriptor = MagicMock()
    plant_descriptor.plant_id = "test_plant"
    plant_descriptor.devices = []
    
    # Crea il consumer
    consumer = DataCollectorConsumer(plant_descriptor, "test_path/")
    
    # Mock del metodo di elaborazione
    consumer._process_message_async = MagicMock()
    
    # Avvia il consumer
    consumer.running = True
    
    # Avvia il thread di elaborazione
    processing_thread = threading.Thread(target=consumer._message_processor_thread, daemon=True)
    processing_thread.start()
    
    # Aggiungi alcuni messaggi alla queue
    for i in range(5):
        test_message = {
            'topic': f'test/topic/{i}',
            'payload': f'{{"test": "data_{i}"}}',
            'sensor_type': 'humidity',
            'value': 50.0 + i,
            'device_name': 'test_device',
            'timestamp': int(time.time())
        }
        consumer.message_queue.put(test_message)
    
    # Attendi che i messaggi vengano elaborati
    time.sleep(2)
    
    # Ferma il consumer
    consumer.running = False
    processing_thread.join(timeout=5.0)
    
    # Verifica che i messaggi siano stati elaborati
    if consumer.message_queue.empty():
        print("   ✅ PASS: Tutti i messaggi elaborati")
        return True
    else:
        print("   ❌ FAIL: Alcuni messaggi non elaborati")
        return False

def main():
    """
    Esegue tutti i test di performance.
    """
    print("🚀 Test di Ottimizzazione Performance DataCollectorConsumer")
    print("=" * 60)
    
    tests = [
        test_on_message_performance,
        test_message_queue_functionality,
        test_thread_safety
    ]
    
    passed = 0
    total = len(tests)
    
    for test in tests:
        try:
            if test():
                passed += 1
        except Exception as e:
            print(f"   ❌ ERROR: {e}")
    
    print("\n" + "=" * 60)
    print(f"📊 Risultati: {passed}/{total} test passati")
    
    if passed == total:
        print("🎉 Tutti i test sono passati! L'ottimizzazione è efficace.")
        return True
    else:
        print("⚠️  Alcuni test sono falliti. Controlla l'implementazione.")
        return False

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
