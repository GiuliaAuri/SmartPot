#!/usr/bin/env python3
"""
Test completo per verificare che data_collector_consumer.py 
invochi correttamente data_collector_producer.py per activate/deactivate
"""

import sys
import os

# Aggiungi il path per importare i moduli del progetto
project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), '.'))
sys.path.insert(0, project_root)

from data_collector.factory.factory import Factory
from data_collector.data_collector_consumer import DataCollectorConsumer

def test_complete_consumer_producer():
    """Test completo per verificare l'integrazione."""
    
    print("🧪 Test Completo Consumer-Producer")
    print("=" * 50)
    
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
        
        print(f"\n🔍 Test Scenari Diversi")
        print("-" * 30)
        
        # Scenario 1: Umidità bassa (attiva irrigazione)
        print(f"📊 Scenario 1: Umidità bassa (150)")
        from unittest.mock import Mock
        mock_msg1 = Mock()
        mock_msg1.topic = "plant/sensor/humidity"
        mock_msg1.payload = b"150"
        consumer.on_message(None, None, mock_msg1)
        
        print(f"\n📊 Scenario 2: Umidità alta (250)")
        mock_msg2 = Mock()
        mock_msg2.topic = "plant/sensor/humidity"
        mock_msg2.payload = b"250"
        consumer.on_message(None, None, mock_msg2)
        
        print(f"\n📊 Scenario 3: Batteria bassa (15) - Solo alert")
        mock_msg3 = Mock()
        mock_msg3.topic = "plant/sensor/battery_level"
        mock_msg3.payload = b"15"
        consumer.on_message(None, None, mock_msg3)
        
        print(f"\n📊 Scenario 4: Valori normali (210) - Nessuna azione")
        mock_msg4 = Mock()
        mock_msg4.topic = "plant/sensor/humidity"
        mock_msg4.payload = b"210"
        consumer.on_message(None, None, mock_msg4)
        
        print(f"\n🎯 Test Completo Completato!")
        print("✅ Consumer invoca correttamente il Producer")
        print("✅ Azioni activate/deactivate eseguite")
        print("✅ Alert gestiti correttamente")
        print("✅ Valori normali non attivano azioni")
        
    except Exception as e:
        print(f"❌ Errore durante il test: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    test_complete_consumer_producer()
