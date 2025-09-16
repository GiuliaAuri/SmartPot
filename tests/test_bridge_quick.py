#!/usr/bin/env python3
"""
Test rapido per verificare il funzionamento del bridge_Serial_MQTT.py
"""

import time
import paho.mqtt.publish as publish
import paho.mqtt.client as mqtt
import threading
import sys
import os

# Aggiungi il path per importare i moduli del progetto
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

import conf.mqtt_conf_params as mqtt_conf_params

class QuickBridgeTest:
    """Test rapido del bridge"""
    
    def __init__(self):
        self.broker_host = "localhost"
        self.broker_port = 7883
        self.messages_received = []
        
    def setup_mqtt_subscriber(self):
        """Configura subscriber MQTT per monitorare i messaggi"""
        def on_connect(client, userdata, flags, rc):
            print(f"📡 Connesso al broker MQTT (codice: {rc})")
            # Sottoscrivi ai topic dei sensori
            client.subscribe("plant/+/device/+/telemetry/+")
            client.subscribe("plant/sensor/+")
            
        def on_message(client, userdata, msg):
            message = f"📨 Ricevuto - Topic: {msg.topic}, Payload: {msg.payload.decode()}"
            print(message)
            self.messages_received.append((msg.topic, msg.payload.decode()))
            
        self.client = mqtt.Client()
        self.client.on_connect = on_connect
        self.client.on_message = on_message
        
        try:
            self.client.connect(self.broker_host, self.broker_port, 60)
            self.client.loop_start()
            print("✅ Subscriber MQTT avviato")
            return True
        except Exception as e:
            print(f"❌ Errore connessione MQTT: {e}")
            return False
    
    def test_actuator_commands(self):
        """Testa i comandi per gli attuatori"""
        print("\n🎮 TEST COMANDI ATTUATORI")
        print("-" * 30)
        
        # Topic di comando per irrigazione
        command_topic = mqtt_conf_params.MqttConfigurationParameters.build_command_plant_topic("irrigation")
        print(f"📡 Topic comando: {command_topic}")
        
        # Test comandi di attivazione
        print("\n✅ Test ATTIVAZIONE:")
        activation_commands = ["start", "on", "1"]
        
        for cmd in activation_commands:
            print(f"   Invio: '{cmd}'")
            try:
                publish.single(command_topic, cmd, hostname=self.broker_host, port=self.broker_port)
                print(f"   ✅ Inviato")
                time.sleep(1)
            except Exception as e:
                print(f"   ❌ Errore: {e}")
        
        time.sleep(2)
        
        # Test comandi di disattivazione
        print("\n❌ Test DISATTIVAZIONE:")
        deactivation_commands = ["stop", "off", "0"]
        
        for cmd in deactivation_commands:
            print(f"   Invio: '{cmd}'")
            try:
                publish.single(command_topic, cmd, hostname=self.broker_host, port=self.broker_port)
                print(f"   ✅ Inviato")
                time.sleep(1)
            except Exception as e:
                print(f"   ❌ Errore: {e}")
        
        # Test comando non riconosciuto
        print("\n⚠️ Test comando NON RICONOSCIUTO:")
        try:
            publish.single(command_topic, "unknown", hostname=self.broker_host, port=self.broker_port)
            print("   ✅ Inviato (dovrebbe essere ignorato)")
        except Exception as e:
            print(f"   ❌ Errore: {e}")
    
    def monitor_sensor_data(self, duration=30):
        """Monitora i dati dei sensori per un periodo di tempo"""
        print(f"\n📊 MONITORAGGIO DATI SENSORI ({duration}s)")
        print("-" * 40)
        
        start_time = time.time()
        initial_count = len(self.messages_received)
        
        while time.time() - start_time < duration:
            time.sleep(1)
            current_count = len(self.messages_received)
            if current_count > initial_count:
                print(f"📈 Messaggi ricevuti: {current_count - initial_count}")
                initial_count = current_count
        
        print(f"\n📋 Riepilogo messaggi ricevuti:")
        for i, (topic, payload) in enumerate(self.messages_received[-10:], 1):  # Ultimi 10
            print(f"   {i}. {topic}: {payload}")
    
    def run_test(self):
        """Esegue il test completo"""
        print("🚀 TEST RAPIDO BRIDGE-ARDUINO")
        print("=" * 40)
        
        # Setup subscriber MQTT
        if not self.setup_mqtt_subscriber():
            print("❌ Impossibile avviare subscriber MQTT")
            return False
        
        # Test comandi attuatori
        self.test_actuator_commands()
        
        # Monitora dati sensori
        self.monitor_sensor_data(20)
        
        # Riepilogo finale
        print(f"\n📊 RIEPILOGO FINALE:")
        print(f"   Messaggi ricevuti: {len(self.messages_received)}")
        
        if self.messages_received:
            print("   ✅ Test completato con successo!")
            return True
        else:
            print("   ⚠️ Nessun messaggio ricevuto - verifica che il bridge sia attivo")
            return False

def main():
    """Funzione principale"""
    print("🧪 TEST RAPIDO BRIDGE SERIAL MQTT")
    print("\nPrima di avviare il test:")
    print("1. Assicurati che il broker MQTT sia attivo")
    print("2. Avvia il bridge_Serial_MQTT.py")
    print("3. Collega Arduino (opzionale)")
    
    input("\nPremi INVIO per continuare...")
    
    tester = QuickBridgeTest()
    success = tester.run_test()
    
    if success:
        print("\n🎉 Test completato con successo!")
    else:
        print("\n❌ Test fallito - controlla la configurazione")

if __name__ == "__main__":
    main()

