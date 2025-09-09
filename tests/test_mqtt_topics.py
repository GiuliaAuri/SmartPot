#!/usr/bin/env python3
"""
Script per testare i topic MQTT del sistema Plants-System
"""

import paho.mqtt.client as mqtt
import json
import time
import sys

class MQTTTester:
    def __init__(self, broker_host="localhost", broker_port=1883):
        self.broker_host = broker_host
        self.broker_port = broker_port
        self.client = mqtt.Client()
        self.client.on_connect = self.on_connect
        self.client.on_message = self.on_message
        self.client.on_disconnect = self.on_disconnect
        
    def on_connect(self, client, userdata, flags, rc):
        if rc == 0:
            print(f"✅ Connesso al broker MQTT {self.broker_host}:{self.broker_port}")
        else:
            print(f"❌ Errore connessione: {rc}")
            
    def on_message(self, client, userdata, msg):
        try:
            topic = msg.topic
            payload = msg.payload.decode('utf-8')
            
            print(f"\n📡 Topic: {topic}")
            print(f"📄 Payload: {payload}")
            
            # Prova a formattare come JSON se possibile
            try:
                json_data = json.loads(payload)
                print(f"📋 JSON formattato:")
                print(json.dumps(json_data, indent=2, ensure_ascii=False))
            except json.JSONDecodeError:
                print(f"📄 Testo semplice: {payload}")
                
        except Exception as e:
            print(f"❌ Errore nel processare il messaggio: {e}")
            
    def on_disconnect(self, client, userdata, rc):
        print(f"🔌 Disconnesso dal broker (codice: {rc})")
        
    def subscribe_to_topic(self, topic):
        """Sottoscrivi a un topic specifico"""
        print(f"🔍 Sottoscrizione al topic: {topic}")
        result = self.client.subscribe(topic)
        if result[0] == mqtt.MQTT_ERR_SUCCESS:
            print(f"✅ Sottoscrizione riuscita a {topic}")
        else:
            print(f"❌ Errore sottoscrizione: {result}")
            
    def subscribe_to_wildcard(self, pattern):
        """Sottoscrivi a un pattern wildcard"""
        print(f"🔍 Sottoscrizione al pattern: {pattern}")
        result = self.client.subscribe(pattern)
        if result[0] == mqtt.MQTT_ERR_SUCCESS:
            print(f"✅ Sottoscrizione riuscita a {pattern}")
        else:
            print(f"❌ Errore sottoscrizione: {result}")
            
    def publish_message(self, topic, message):
        """Pubblica un messaggio su un topic"""
        print(f"📤 Pubblicazione su {topic}: {message}")
        result = self.client.publish(topic, message)
        if result[0] == mqtt.MQTT_ERR_SUCCESS:
            print(f"✅ Messaggio pubblicato con successo")
        else:
            print(f"❌ Errore pubblicazione: {result}")
            
    def start_listening(self, duration=30):
        """Inizia ad ascoltare per un periodo specificato"""
        print(f"👂 Inizio ascolto per {duration} secondi...")
        print("Premi Ctrl+C per interrompere")
        
        try:
            self.client.loop_start()
            time.sleep(duration)
        except KeyboardInterrupt:
            print("\n⏹️ Interruzione manuale")
        finally:
            self.client.loop_stop()
            self.client.disconnect()
            
    def connect(self):
        """Connetti al broker"""
        try:
            self.client.connect(self.broker_host, self.broker_port, 60)
            return True
        except Exception as e:
            print(f"❌ Errore connessione: {e}")
            return False

def main():
    print("🌱 MQTT Tester per Plants-System")
    print("=" * 50)
    
    # Crea il tester
    tester = MQTTTester()
    
    # Connetti al broker
    if not tester.connect():
        print("❌ Impossibile connettersi al broker MQTT")
        print("   Assicurati che il broker sia in esecuzione")
        return
    
    # Menu interattivo
    while True:
        print("\n🔧 Menu MQTT Tester:")
        print("1. Sottoscrivi a topic specifico (es: plant/my_fico1/info)")
        print("2. Sottoscrivi a pattern wildcard (es: plant/+/info)")
        print("3. Sottoscrivi a tutti i topic delle piante")
        print("4. Sottoscrivi solo alla telemetria")
        print("5. Sottoscrivi solo ai comandi")
        print("6. Pubblica messaggio di test")
        print("0. Esci")
        
        choice = input("\nScegli un'opzione (0-6): ").strip()
        
        if choice == "0":
            break
        elif choice == "1":
            topic = input("Inserisci il topic (es: plant/my_fico1/info): ").strip()
            if topic:
                tester.subscribe_to_topic(topic)
                tester.start_listening(30)
        elif choice == "2":
            pattern = input("Inserisci il pattern (es: plant/+/info): ").strip()
            if pattern:
                tester.subscribe_to_wildcard(pattern)
                tester.start_listening(30)
        elif choice == "3":
            tester.subscribe_to_wildcard("plant/+/+")
            tester.start_listening(30)
        elif choice == "4":
            tester.subscribe_to_wildcard("plant/+/+/telemetry/+")
            tester.start_listening(30)
        elif choice == "5":
            tester.subscribe_to_wildcard("plant/+/+/command/+")
            tester.start_listening(30)
        elif choice == "6":
            topic = input("Inserisci il topic: ").strip()
            message = input("Inserisci il messaggio: ").strip()
            if topic and message:
                tester.publish_message(topic, message)
        else:
            print("❌ Opzione non valida")
    
    print("👋 Arrivederci!")

if __name__ == "__main__":
    main()
