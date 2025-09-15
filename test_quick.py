#!/usr/bin/env python3
"""
Test rapido per verificare se i componenti sono attivi.
"""

import paho.mqtt.client as mqtt
import time
import sys
import os

# Aggiungi il path per importare i moduli del progetto
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from conf.mqtt_conf_params import MqttConfigurationParameters

def quick_test():
    """Test rapido del sistema"""
    print("🔍 TEST RAPIDO SISTEMA")
    print("=" * 30)
    
    broker_host = MqttConfigurationParameters.BROKER_ADDRESS
    broker_port = MqttConfigurationParameters.BROKER_PORT
    
    messages_received = []
    
    def on_connect(client, userdata, flags, rc):
        if rc == 0:
            print("✅ Connesso al broker MQTT")
            # Sottoscrivi ai topic principali
            client.subscribe("plant/sensor/+")
            client.subscribe("plant/actuator/+")
        else:
            print(f"❌ Errore connessione: {rc}")
    
    def on_message(client, userdata, msg):
        print(f"📨 {msg.topic}: {msg.payload.decode()}")
        messages_received.append((msg.topic, msg.payload.decode()))
    
    # Setup client
    client = mqtt.Client()
    client.on_connect = on_connect
    client.on_message = on_message
    
    try:
        print("🔌 Connessione al broker...")
        client.connect(broker_host, broker_port, 60)
        client.loop_start()
        
        print("⏳ Monitoraggio per 10 secondi...")
        time.sleep(10)
        
        client.loop_stop()
        client.disconnect()
        
        print(f"\n📊 RISULTATI:")
        print(f"   Messaggi ricevuti: {len(messages_received)}")
        
        if messages_received:
            print("   ✅ Sistema attivo!")
            for topic, payload in messages_received:
                print(f"   - {topic}: {payload}")
        else:
            print("   ⚠️ Nessun messaggio - Componenti potrebbero non essere attivi")
            
    except Exception as e:
        print(f"❌ Errore: {e}")

if __name__ == "__main__":
    quick_test()
