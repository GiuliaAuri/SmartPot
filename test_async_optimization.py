#!/usr/bin/env python3
"""
Test per verificare l'ottimizzazione async del DataCollectorConsumer.

Questo script testa che il callback on_message sia veloce e che le operazioni
async funzionino correttamente.
"""

import time
import json
import asyncio
import threading
from unittest.mock import MagicMock, patch
import sys
import os

# Aggiungi il path del progetto
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from plants_system.smart_objects.models.plant_descriptor import PlantDescriptor
from plants_system.process.data_collector_consumer import DataCollectorConsumer

def test_on_message_performance_async():
    """
    Testa che il callback on_message sia veloce (< 5ms) con async.
    """
    print("🧪 Test: Performance del callback on_message con async")
    
    # Crea un PlantDescriptor mock
    plant_descriptor = MagicMock()
    plant_descriptor.plant_id = "test_plant"
    plant_descriptor.devices = []
    
    # Crea il consumer
    consumer = DataCollectorConsumer(plant_descriptor, "test_path/")
    
    # Avvia l'event loop asyncio in un thread separato
    def run_async_loop():
        consumer.loop = asyncio.new_event_loop()
        asyncio.set_event_loop(consumer.loop)
        consumer.loop.run_forever()
    
    async_thread = threading.Thread(target=run_async_loop, daemon=True)
    async_thread.start()
    
    # Attendi che l'event loop sia pronto
    time.sleep(0.1)
    
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
    
    # Ferma l'event loop
    if consumer.loop and not consumer.loop.is_closed():
        consumer.loop.call_soon_threadsafe(consumer.loop.stop)
    async_thread.join(timeout=5.0)
    
    # Verifica che sia veloce (< 5ms per messaggio)
    if avg_time < 5:
        print("   ✅ PASS: Callback on_message è veloce con async")
        return True
    else:
        print("   ❌ FAIL: Callback on_message è troppo lento")
        return False

def test_async_operations():
    """
    Testa che le operazioni async funzionino correttamente.
    """
    print("\n🧪 Test: Operazioni async")
    
    # Crea un PlantDescriptor mock
    plant_descriptor = MagicMock()
    plant_descriptor.plant_id = "test_plant"
    plant_descriptor.devices = []
    
    # Crea il consumer
    consumer = DataCollectorConsumer(plant_descriptor, "test_path/")
    
    # Mock dei metodi
    consumer.update_sensor_history = MagicMock()
    consumer.policy_manager.evaluate = MagicMock()
    consumer.update_alerts_history = MagicMock()
    consumer.update_actuator_history = MagicMock()
    consumer._get_current_actuator_state = MagicMock(return_value=False)
    consumer._send_command_sync = MagicMock()
    
    # Avvia l'event loop asyncio
    def run_async_loop():
        consumer.loop = asyncio.new_event_loop()
        asyncio.set_event_loop(consumer.loop)
        consumer.loop.run_forever()
    
    async_thread = threading.Thread(target=run_async_loop, daemon=True)
    async_thread.start()
    
    # Attendi che l'event loop sia pronto
    time.sleep(0.1)
    
    # Testa l'elaborazione async
    message_data = {
        'topic': 'test/topic',
        'payload': '{"test": "data"}',
        'sensor_type': 'humidity',
        'value': 50.0,
        'device_name': 'test_device',
        'timestamp': int(time.time())
    }
    
    # Esegui l'elaborazione async
    future = asyncio.run_coroutine_threadsafe(
        consumer._process_message_async(message_data), 
        consumer.loop
    )
    
    # Attendi il completamento
    try:
        future.result(timeout=5.0)
        print("   ✅ PASS: Elaborazione async completata")
        
        # Verifica che i metodi siano stati chiamati
        if consumer.update_sensor_history.called:
            print("   ✅ PASS: update_sensor_history chiamato")
        else:
            print("   ❌ FAIL: update_sensor_history non chiamato")
            return False
            
        if consumer.policy_manager.evaluate.called:
            print("   ✅ PASS: policy_manager.evaluate chiamato")
        else:
            print("   ❌ FAIL: policy_manager.evaluate non chiamato")
            return False
            
        return True
        
    except Exception as e:
        print(f"   ❌ FAIL: Errore nell'elaborazione async: {e}")
        return False
    finally:
        # Ferma l'event loop
        if consumer.loop and not consumer.loop.is_closed():
            consumer.loop.call_soon_threadsafe(consumer.loop.stop)
        async_thread.join(timeout=5.0)

def test_thread_pool_executor():
    """
    Testa che il ThreadPoolExecutor funzioni correttamente.
    """
    print("\n🧪 Test: ThreadPoolExecutor")
    
    # Crea un PlantDescriptor mock
    plant_descriptor = MagicMock()
    plant_descriptor.plant_id = "test_plant"
    plant_descriptor.devices = []
    
    # Crea il consumer
    consumer = DataCollectorConsumer(plant_descriptor, "test_path/")
    
    # Mock dei metodi
    consumer.update_sensor_history = MagicMock()
    
    # Avvia l'event loop asyncio
    def run_async_loop():
        consumer.loop = asyncio.new_event_loop()
        asyncio.set_event_loop(consumer.loop)
        consumer.loop.run_forever()
    
    async_thread = threading.Thread(target=run_async_loop, daemon=True)
    async_thread.start()
    
    # Attendi che l'event loop sia pronto
    time.sleep(0.1)
    
    # Testa l'esecuzione nel thread pool
    async def test_executor():
        await consumer._update_sensor_history_async('humidity', 50.0, 'test_device')
        return True
    
    # Esegui il test
    future = asyncio.run_coroutine_threadsafe(test_executor(), consumer.loop)
    
    try:
        result = future.result(timeout=5.0)
        if result and consumer.update_sensor_history.called:
            print("   ✅ PASS: ThreadPoolExecutor funziona correttamente")
            return True
        else:
            print("   ❌ FAIL: ThreadPoolExecutor non funziona")
            return False
    except Exception as e:
        print(f"   ❌ FAIL: Errore nel ThreadPoolExecutor: {e}")
        return False
    finally:
        # Ferma l'event loop
        if consumer.loop and not consumer.loop.is_closed():
            consumer.loop.call_soon_threadsafe(consumer.loop.stop)
        async_thread.join(timeout=5.0)

def main():
    """
    Esegue tutti i test di ottimizzazione async.
    """
    print("🚀 Test di Ottimizzazione Async DataCollectorConsumer")
    print("=" * 60)
    
    tests = [
        test_on_message_performance_async,
        test_async_operations,
        test_thread_pool_executor
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
        print("🎉 Tutti i test sono passati! L'ottimizzazione async è efficace.")
        return True
    else:
        print("⚠️  Alcuni test sono falliti. Controlla l'implementazione.")
        return False

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
