#!/usr/bin/env python3
"""
Test per verificare la comunicazione tra i componenti del sistema.
"""

import paho.mqtt.client as mqtt
import time
import sys
import os

# Aggiungi il path per importare i moduli del progetto
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from conf.mqtt_conf_params import MqttConfigurationParameters

class SystemTester:
    """Testa la comunicazione tra i componenti del sistema"""
    
    def __init__(self):
        self.broker_host = MqttConfigurationParameters.BROKER_ADDRESS
        self.broker_port = MqttConfigurationParameters.BROKER_PORT
        self.messages_received = []
        self.connected = False
        
    def on_connect(self, client, userdata, flags, rc):
        """Callback per la connessione MQTT"""
        if rc == 0:
            print("✅ Connesso al broker MQTT")
            self.connected = True
            
            # Sottoscrivi ai topic dei sensori per monitorare i dati
            sensor_topics = [
                "plant/sensor/humidity",
                "plant/sensor/temperature", 
                "plant/sensor/lightness",
                "plant/sensor/battery_level"
            ]
            
            for topic in sensor_topics:
                client.subscribe(topic)
                print(f"📡 Sottoscritto a: {topic}")
                
        else:
            print(f"❌ Errore connessione MQTT: {rc}")
    
    def on_message(self, client, userdata, msg):
        """Callback per i messaggi ricevuti"""
        message = f"📨 Ricevuto - Topic: {msg.topic}, Payload: {msg.payload.decode()}"
        print(message)
        self.messages_received.append((msg.topic, msg.payload.decode()))
    
    def test_sensor_data(self, duration=10):
        """Testa la ricezione di dati dai sensori"""
        print(f"\n📊 TEST DATI SENSORI ({duration}s)")
        print("-" * 40)
        
        # Setup client MQTT
        client = mqtt.Client()
        client.on_connect = self.on_connect
        client.on_message = self.on_message
        
        try:
            client.connect(self.broker_host, self.broker_port, 60)
            client.loop_start()
            
            # Attendi connessione
            time.sleep(1)
            
            if not self.connected:
                print("❌ Impossibile connettersi al broker MQTT")
                return False
            
            # Monitora per il tempo specificato
            start_time = time.time()
            while time.time() - start_time < duration:
                time.sleep(1)
            
            client.loop_stop()
            client.disconnect()
            
            # Risultati
            print(f"\n📋 RISULTATI:")
            print(f"   Messaggi ricevuti: {len(self.messages_received)}")
            
            if self.messages_received:
                print("   ✅ Bridge attivo e invia dati!")
                for topic, payload in self.messages_received[-5:]:  # Ultimi 5
                    print(f"   - {topic}: {payload}")
                return True
            else:
                print("   ⚠️ Nessun dato ricevuto - Bridge potrebbe non essere attivo")
                return False
                
        except Exception as e:
            print(f"❌ Errore test sensori: {e}")
            return False
    
    def test_actuator_command(self):
        """Testa l'invio di comandi agli attuatori"""
        print(f"\n🎮 TEST COMANDI ATTUATORI")
        print("-" * 30)
        
        command_topic = MqttConfigurationParameters.build_command_plant_topic("irrigation")
        print(f"📡 Topic comando: {command_topic}")
        
        # Test comando di attivazione
        print("   Invio comando: 'start'")
        try:
            import paho.mqtt.publish as publish
            publish.single(command_topic, "start", hostname=self.broker_host, port=self.broker_port)
            print("   ✅ Comando inviato")
            time.sleep(1)
            
            # Test comando di disattivazione
            print("   Invio comando: 'stop'")
            publish.single(command_topic, "stop", hostname=self.broker_host, port=self.broker_port)
            print("   ✅ Comando inviato")
            
            return True
            
        except Exception as e:
            print(f"   ❌ Errore invio comando: {e}")
            return False
    
    def check_components_status(self):
        """Verifica lo stato dei componenti"""
        print("🔍 VERIFICA STATO COMPONENTI")
        print("=" * 50)
        
        # Test 1: Broker MQTT
        print("\n1️⃣ Test Broker MQTT:")
        try:
            client = mqtt.Client()
            client.connect(self.broker_host, self.broker_port, 60)
            client.disconnect()
            print("   ✅ Broker MQTT attivo")
            broker_ok = True
        except Exception as e:
            print(f"   ❌ Broker MQTT non raggiungibile: {e}")
            broker_ok = False
        
        # Test 2: Dati sensori
        print("\n2️⃣ Test Dati Sensori:")
        sensors_ok = self.test_sensor_data(5)
        
        # Test 3: Comandi attuatori
        print("\n3️⃣ Test Comandi Attuatori:")
        actuators_ok = self.test_actuator_command()
        
        # Riepilogo
        print(f"\n📊 RIEPILOGO:")
        print(f"   Broker MQTT: {'✅' if broker_ok else '❌'}")
        print(f"   Bridge (sensori): {'✅' if sensors_ok else '❌'}")
        print(f"   Bridge (attuatori): {'✅' if actuators_ok else '❌'}")
        
        if broker_ok and sensors_ok and actuators_ok:
            print("\n🎉 TUTTI I COMPONENTI ATTIVI E FUNZIONANTI!")
            return True
        else:
            print("\n⚠️ ALCUNI COMPONENTI NON FUNZIONANO")
            return False

def main():
    """Funzione principale"""
    print("🧪 TEST SISTEMA PLANTS-SYSTEM")
    print("=" * 50)
    
    tester = SystemTester()
    
    print("Prima di avviare il test:")
    print("1. Assicurati che il broker MQTT sia attivo")
    print("2. Avvia il bridge: python bridge\\bridge_Serial_MQTT.py")
    print("3. Avvia il data collector: python data_collector\\data_collector_main.py")
    
    input("\nPremi INVIO per continuare...")
    
    success = tester.check_components_status()
    
    if success:
        print("\n🎉 Sistema completamente funzionale!")
    else:
        print("\n❌ Sistema ha problemi - controlla i componenti")

if __name__ == "__main__":
    main()
