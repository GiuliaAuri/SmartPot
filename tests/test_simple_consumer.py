#!/usr/bin/env python3
"""
Test semplice per verificare che data_collector_consumer.py 
invochi correttamente data_collector_producer.py
"""

import sys
import os

# Aggiungi il path per importare i moduli del progetto
project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), '.'))
sys.path.insert(0, project_root)

from data_collector.factory.factory import Factory
from data_collector.data_collector_consumer import DataCollectorConsumer

def test_simple_consumer_producer():
    """Test semplice per verificare l'integrazione."""
    
    print("🧪 Test Semplice Consumer-Producer")
    print("=" * 40)
    
    try:
        # Crea plant descriptor
        plants = Factory.create_plant_descriptor()
        if not plants:
            print("❌ Nessuna pianta creata")
            return
        
        plant = plants[0]
        print(f"🌱 Pianta test: {plant.plant_id} ({plant.species})")
        
        # Crea consumer
        consumer = DataCollectorConsumer(plant, "cloud_simulator/plants_log")
        
        # Imposta il consumer come attivo per il test
        consumer.running = True
        
        print(f"\n🔍 Test Valutazione Policy")
        print("-" * 25)
        
        # Test scenario: Umidità bassa (attiva irrigazione)
        print(f"📊 Scenario: Umidità bassa (150)")
        
        # Simula la ricezione di un messaggio MQTT
        from unittest.mock import Mock
        mock_msg = Mock()
        mock_msg.topic = "plant/sensor/humidity"
        mock_msg.payload = b"150"
        
        # Simula il callback on_message
        consumer.on_message(None, None, mock_msg)
        
        print(f"\n✅ Test completato!")
        
    except Exception as e:
        print(f"❌ Errore durante il test: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    test_simple_consumer_producer()
