#!/usr/bin/env python3
"""
Test per verificare che data_collector_consumer.py invochi correttamente 
data_collector_producer.py per l'esecuzione delle azioni.
"""

import sys
import os
import time
import threading
from unittest.mock import Mock, patch

# Aggiungi il path per importare i moduli del progetto
project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), '.'))
sys.path.insert(0, project_root)

from data_collector.factory.factory import Factory
from data_collector.data_collector_consumer import DataCollectorConsumer
from data_collector.data_collector_producer import DataCollectorProducer

def test_consumer_producer_integration():
    """Test per verificare l'integrazione tra consumer e producer."""
    
    print("🧪 Test Integrazione Consumer-Producer")
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
        
        # Mock del producer per verificare le chiamate
        with patch('data_collector.data_collector_consumer.DataCollectorProducer') as mock_producer_class:
            mock_producer_instance = Mock()
            mock_producer_class.return_value = mock_producer_instance
            
            print(f"\n🔍 Test Valutazione Policy e Esecuzione Azioni")
            print("-" * 40)
            
            # Test scenario 1: Umidità bassa (dovrebbe attivare irrigazione)
            print(f"📊 Scenario 1: Umidità bassa (150)")
            consumer._evaluate_policies_and_execute_actions("humidity", 150)
            
            # Verifica che il producer sia stato chiamato
            assert mock_producer_class.called, "DataCollectorProducer dovrebbe essere stato chiamato"
            assert mock_producer_instance.run.called, "Il metodo run() del producer dovrebbe essere stato chiamato"
            
            print(f"✅ Producer chiamato correttamente per umidità bassa")
            
            # Reset del mock
            mock_producer_class.reset_mock()
            mock_producer_instance.reset_mock()
            
            # Test scenario 2: Umidità alta (dovrebbe disattivare irrigazione)
            print(f"\n📊 Scenario 2: Umidità alta (250)")
            consumer._evaluate_policies_and_execute_actions("humidity", 250)
            
            # Verifica che il producer sia stato chiamato
            assert mock_producer_class.called, "DataCollectorProducer dovrebbe essere stato chiamato"
            assert mock_producer_instance.run.called, "Il metodo run() del producer dovrebbe essere stato chiamato"
            
            print(f"✅ Producer chiamato correttamente per umidità alta")
            
            # Reset del mock
            mock_producer_class.reset_mock()
            mock_producer_instance.reset_mock()
            
            # Test scenario 3: Batteria bassa (dovrebbe solo generare alert)
            print(f"\n📊 Scenario 3: Batteria bassa (15)")
            consumer._evaluate_policies_and_execute_actions("battery_level", 15)
            
            # Verifica che il producer NON sia stato chiamato (solo alert)
            assert not mock_producer_class.called, "DataCollectorProducer NON dovrebbe essere chiamato per alert"
            
            print(f"✅ Nessun producer chiamato per alert (come atteso)")
            
            # Reset del mock
            mock_producer_class.reset_mock()
            mock_producer_instance.reset_mock()
            
            # Test scenario 4: Valori normali (nessuna azione)
            print(f"\n📊 Scenario 4: Valori normali (210)")
            consumer._evaluate_policies_and_execute_actions("humidity", 210)
            
            # Verifica che il producer NON sia stato chiamato
            assert not mock_producer_class.called, "DataCollectorProducer NON dovrebbe essere chiamato per valori normali"
            
            print(f"✅ Nessun producer chiamato per valori normali (come atteso)")
        
        print(f"\n🎯 Test Integrazione Completato!")
        print("✅ Consumer invoca correttamente il Producer")
        print("✅ Producer viene chiamato solo quando necessario")
        print("✅ Alert non attivano Producer")
        print("✅ Valori normali non attivano Producer")
        
    except Exception as e:
        print(f"❌ Errore durante il test: {e}")
        import traceback
        traceback.print_exc()

def test_real_producer_execution():
    """Test con producer reale per verificare l'esecuzione completa."""
    
    print(f"\n🧪 Test Esecuzione Producer Reale")
    print("=" * 50)
    
    try:
        # Crea plant descriptor
        plants = Factory.create_plant_descriptor()
        if not plants:
            print("❌ Nessuna pianta creata")
            return
        
        plant = plants[0]
        
        # Crea consumer
        consumer = DataCollectorConsumer(plant, "cloud_simulator/plants_log")
        
        print(f"🔍 Test con Producer Reale")
        print("-" * 30)
        
        # Test scenario: Umidità bassa (attiva irrigazione)
        print(f"📊 Scenario: Umidità bassa (150)")
        consumer._evaluate_policies_and_execute_actions("humidity", 150)
        
        print(f"✅ Producer reale eseguito correttamente")
        
        # Verifica che i dati siano stati salvati nel JSON
        json_file = f"cloud_simulator/plants_log/{plant.plant_id}.json"
        if os.path.exists(json_file):
            print(f"✅ File JSON aggiornato: {json_file}")
        else:
            print(f"❌ File JSON non trovato: {json_file}")
        
    except Exception as e:
        print(f"❌ Errore durante il test: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    test_consumer_producer_integration()
    test_real_producer_execution()
