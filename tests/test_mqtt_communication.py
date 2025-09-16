#!/usr/bin/env python3
"""
Test per verificare la comunicazione MQTT tra bridge e data collector.
"""

import paho.mqtt.client as mqtt
import time
import threading

def test_mqtt_communication():
    """Test della comunicazione MQTT."""
    
    print("🧪 Test comunicazione MQTT")
    print("=" * 50)
    
    # Configurazione MQTT
    BROKER_ADDRESS = "127.0.0.1"
    BROKER_PORT = 7883
    
    # Topic di test
    test_topics = [
        "plant/sensor/humidity",
        "plant/sensor/temperature", 
        "plant/sensor/lightness",
        "plant/sensor/battery_level"
    ]
    
    # Valori di test
    test_values = [65, 25, 500, 85]
    
    # Callback per i messaggi ricevuti
    received_messages = []
    
    def on_connect(client, userdata, flags, rc):
        print(f"✅ Connesso al broker MQTT (codice: {rc})")
        
        # Sottoscriviti a tutti i topic di test
        for topic in test_topics:
            client.subscribe(topic)
            print(f"🔔 Sottoscritto a: {topic}")
    
    def on_message(client, userdata, msg):
        message = f"📨 Ricevuto - Topic: {msg.topic}, Payload: {msg.payload.decode()}"
        print(message)
        received_messages.append(message)
    
    # Crea client MQTT
    client = mqtt.Client()
    client.on_connect = on_connect
    client.on_message = on_message
    
    try:
        # Connetti al broker
        print("🔌 Connessione al broker MQTT...")
        client.connect(BROKER_ADDRESS, BROKER_PORT, 60)
        client.loop_start()
        
        # Aspetta la connessione
        time.sleep(2)
        
        # Pubblica messaggi di test
        print("\n📤 Invio messaggi di test...")
        for i, (topic, value) in enumerate(zip(test_topics, test_values)):
            client.publish(topic, str(value))
            print(f"📤 Inviato - Topic: {topic}, Payload: {value}")
            time.sleep(1)
        
        # Aspetta la ricezione
        print("\n⏳ Attesa ricezione messaggi...")
        time.sleep(3)
        
        # Risultati
        print(f"\n📊 Risultati:")
        print(f"   Messaggi inviati: {len(test_topics)}")
        print(f"   Messaggi ricevuti: {len(received_messages)}")
        
        if len(received_messages) == len(test_topics):
            print("✅ Test PASSATO - Tutti i messaggi ricevuti!")
        else:
            print("❌ Test FALLITO - Alcuni messaggi non ricevuti")
            print("   Verifica che il broker MQTT sia attivo")
            print("   Verifica che non ci siano altri client che interferiscono")
        
    except Exception as e:
        print(f"❌ Errore durante il test: {e}")
    
    finally:
        client.loop_stop()
        client.disconnect()
        print("🔌 Disconnesso dal broker MQTT")

if __name__ == "__main__":
    test_mqtt_communication()
