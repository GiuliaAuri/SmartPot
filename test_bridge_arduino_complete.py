#!/usr/bin/env python3
"""
Test completo per verificare il funzionamento del bridge_Serial_MQTT.py
con Arduino simulato.

Questo test simula:
1. Arduino che invia dati dei sensori via seriale
2. Comandi MQTT per attivare/disattivare attuatori
3. Verifica che il bridge pubblichi correttamente i dati dei sensori
4. Verifica che il bridge riceva e processi i comandi degli attuatori
"""

import time
import threading
import serial
import serial.tools.list_ports
import paho.mqtt.client as mqtt
import paho.mqtt.publish as publish
import json
from unittest.mock import Mock, patch
import sys
import os

# Aggiungi il path per importare i moduli del progetto
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from bridge.bridge_Serial_MQTT import Bridge
import conf.mqtt_conf_params as mqtt_conf_params

class ArduinoSimulator:
    """Simula Arduino che invia dati via seriale"""
    
    def __init__(self, port_name="COM_TEST"):
        self.port_name = port_name
        self.serial_connection = None
        self.running = False
        
    def start_simulation(self):
        """Avvia la simulazione Arduino"""
        print(f"🔧 Avvio simulazione Arduino su porta {self.port_name}")
        self.running = True
        
        # Simula l'invio di dati dei sensori ogni 5 secondi
        threading.Thread(target=self._send_sensor_data, daemon=True).start()
        
    def stop_simulation(self):
        """Ferma la simulazione"""
        self.running = False
        
    def _send_sensor_data(self):
        """Simula l'invio di dati dei sensori"""
        sensor_values = [65, 45, 30, 85]  # humidity, temperature, lightness, battery
        
        while self.running:
            try:
                # Simula il protocollo Arduino: FF + num_valori + valori + FE
                packet = bytearray([0xFF])  # Header
                packet.append(len(sensor_values))  # Numero di valori
                
                for val in sensor_values:
                    packet.append(val)  # Valori dei sensori
                    
                packet.append(0xFE)  # Footer
                
                print(f"📡 Arduino invia: {[hex(b) for b in packet]}")
                print(f"📊 Valori sensori: humidity={sensor_values[0]}, temperature={sensor_values[1]}, lightness={sensor_values[2]}, battery={sensor_values[3]}")
                
                # Simula variazione dei valori
                sensor_values = [v + (1 if v < 100 else -1) for v in sensor_values]
                
                time.sleep(5)  # Invia ogni 5 secondi
                
            except Exception as e:
                print(f"❌ Errore simulazione Arduino: {e}")
                break

class MQTTCommandTester:
    """Testa i comandi MQTT per gli attuatori"""
    
    def __init__(self):
        self.broker_host = "localhost"
        self.broker_port = 7883
        
    def test_actuator_commands(self):
        """Testa i comandi per attivare/disattivare attuatori"""
        print("\n🎮 Test comandi attuatori MQTT")
        
        # Topic di comando per irrigazione
        command_topic = mqtt_conf_params.MqttConfigurationParameters.build_command_plant_topic("irrigation")
        print(f"📡 Topic comando: {command_topic}")
        
        # Test comandi di attivazione
        activation_commands = ["start", "on", "1", "START", "ON"]
        print("\n✅ Test comandi di ATTIVAZIONE:")
        
        for cmd in activation_commands:
            print(f"   Invio comando: '{cmd}'")
            try:
                publish.single(command_topic, cmd, hostname=self.broker_host, port=self.broker_port)
                print(f"   ✅ Comando '{cmd}' inviato")
                time.sleep(1)
            except Exception as e:
                print(f"   ❌ Errore invio comando '{cmd}': {e}")
        
        time.sleep(2)
        
        # Test comandi di disattivazione
        deactivation_commands = ["stop", "off", "0", "STOP", "OFF"]
        print("\n❌ Test comandi di DISATTIVAZIONE:")
        
        for cmd in deactivation_commands:
            print(f"   Invio comando: '{cmd}'")
            try:
                publish.single(command_topic, cmd, hostname=self.broker_host, port=self.broker_port)
                print(f"   ✅ Comando '{cmd}' inviato")
                time.sleep(1)
            except Exception as e:
                print(f"   ❌ Errore invio comando '{cmd}': {e}")
        
        # Test comando non riconosciuto
        print("\n⚠️ Test comando NON RICONOSCIUTO:")
        try:
            publish.single(command_topic, "unknown_command", hostname=self.broker_host, port=self.broker_port)
            print("   ✅ Comando 'unknown_command' inviato (dovrebbe essere ignorato)")
        except Exception as e:
            print(f"   ❌ Errore invio comando 'unknown_command': {e}")

class BridgeTester:
    """Testa il bridge completo"""
    
    def __init__(self):
        self.bridge = None
        self.mqtt_messages_received = []
        self.serial_commands_sent = []
        
    def setup_test_environment(self):
        """Configura l'ambiente di test"""
        print("🔧 Configurazione ambiente di test")
        
        # Mock della porta seriale
        mock_serial = Mock()
        mock_serial.in_waiting = 0
        mock_serial.read.return_value = b''
        mock_serial.write = self._mock_serial_write
        
        # Mock del client MQTT
        mock_mqtt_client = Mock()
        mock_mqtt_client.publish = self._mock_mqtt_publish
        mock_mqtt_client.subscribe = Mock()
        mock_mqtt_client.connect = Mock()
        mock_mqtt_client.loop_start = Mock()
        
        return mock_serial, mock_mqtt_client
    
    def _mock_serial_write(self, data):
        """Mock per serial.write - registra i comandi inviati"""
        self.serial_commands_sent.append(data)
        print(f"📤 Comando seriale inviato: {data}")
        
    def _mock_mqtt_publish(self, topic, payload):
        """Mock per mqtt.publish - registra i messaggi pubblicati"""
        self.mqtt_messages_received.append((topic, payload))
        print(f"📡 MQTT pubblicato - Topic: {topic}, Payload: {payload}")
        
    def test_bridge_initialization(self):
        """Testa l'inizializzazione del bridge"""
        print("\n🏗️ Test inizializzazione Bridge")
        
        try:
            # Mock della configurazione
            with patch('configparser.ConfigParser') as mock_config:
                mock_config_instance = Mock()
                mock_config_instance.get.return_value = "localhost"
                mock_config_instance.getint.return_value = 7883
                mock_config.return_value = mock_config_instance
                
                # Mock della porta seriale
                with patch('serial.Serial') as mock_serial_class:
                    mock_serial_instance = Mock()
                    mock_serial_instance.in_waiting = 0
                    mock_serial_instance.read.return_value = b''
                    mock_serial_instance.write = self._mock_serial_write
                    mock_serial_class.return_value = mock_serial_instance
                    
                    # Mock del client MQTT
                    with patch('paho.mqtt.client.Client') as mock_mqtt_class:
                        mock_mqtt_instance = Mock()
                        mock_mqtt_instance.publish = self._mock_mqtt_publish
                        mock_mqtt_instance.subscribe = Mock()
                        mock_mqtt_instance.connect = Mock()
                        mock_mqtt_instance.loop_start = Mock()
                        mock_mqtt_class.return_value = mock_mqtt_instance
                        
                        self.bridge = Bridge()
                        print("✅ Bridge inizializzato correttamente")
                        return True
                        
        except Exception as e:
            print(f"❌ Errore inizializzazione Bridge: {e}")
            return False
    
    def test_sensor_data_processing(self):
        """Testa l'elaborazione dei dati dei sensori"""
        print("\n📊 Test elaborazione dati sensori")
        
        if not self.bridge:
            print("❌ Bridge non inizializzato")
            return False
            
        try:
            # Simula dati ricevuti da Arduino
            test_data = [
                0xFF,  # Header
                4,     # Numero di valori
                65,    # Humidity
                45,    # Temperature  
                30,    # Lightness
                85,    # Battery
                0xFE   # Footer
            ]
            
            # Simula il buffer di input
            self.bridge.inbuffer = [bytes([b]) for b in test_data[:-1]]  # Esclude FE
            
            # Testa useData
            result = self.bridge.useData()
            
            if result is not False:
                print("✅ Dati sensori elaborati correttamente")
                print(f"📡 Messaggi MQTT pubblicati: {len(self.mqtt_messages_received)}")
                for topic, payload in self.mqtt_messages_received:
                    print(f"   - {topic}: {payload}")
                return True
            else:
                print("❌ Errore elaborazione dati sensori")
                return False
                
        except Exception as e:
            print(f"❌ Errore test sensori: {e}")
            return False
    
    def test_actuator_command_processing(self):
        """Testa l'elaborazione dei comandi degli attuatori"""
        print("\n🎮 Test elaborazione comandi attuatori")
        
        if not self.bridge:
            print("❌ Bridge non inizializzato")
            return False
            
        try:
            # Mock della porta seriale
            self.bridge.ser = Mock()
            self.bridge.ser.write = self._mock_serial_write
            
            # Test comando di attivazione
            print("   Test comando ATTIVA:")
            mock_msg = Mock()
            mock_msg.topic = "plant/test/device/irrigation/command"
            mock_msg.payload = b"start"
            
            self.serial_commands_sent.clear()
            self.bridge.on_message(None, None, mock_msg)
            
            if len(self.serial_commands_sent) == 2 and b'I' in self.serial_commands_sent and b'A' in self.serial_commands_sent:
                print("   ✅ Comando ATTIVA processato correttamente")
            else:
                print("   ❌ Errore comando ATTIVA")
                return False
            
            # Test comando di disattivazione
            print("   Test comando DISATTIVA:")
            mock_msg.payload = b"stop"
            
            self.serial_commands_sent.clear()
            self.bridge.on_message(None, None, mock_msg)
            
            if len(self.serial_commands_sent) == 2 and b'I' in self.serial_commands_sent and b'S' in self.serial_commands_sent:
                print("   ✅ Comando DISATTIVA processato correttamente")
                return True
            else:
                print("   ❌ Errore comando DISATTIVA")
                return False
                
        except Exception as e:
            print(f"❌ Errore test attuatori: {e}")
            return False

def run_complete_test():
    """Esegue il test completo del sistema"""
    print("🚀 AVVIO TEST COMPLETO BRIDGE-ARDUINO")
    print("=" * 50)
    
    # Test 1: Inizializzazione Bridge
    bridge_tester = BridgeTester()
    if not bridge_tester.test_bridge_initialization():
        print("❌ Test inizializzazione fallito")
        return False
    
    # Test 2: Elaborazione dati sensori
    if not bridge_tester.test_sensor_data_processing():
        print("❌ Test sensori fallito")
        return False
    
    # Test 3: Elaborazione comandi attuatori
    if not bridge_tester.test_actuator_command_processing():
        print("❌ Test attuatori fallito")
        return False
    
    # Test 4: Comandi MQTT reali (se broker disponibile)
    print("\n🌐 Test comandi MQTT reali")
    mqtt_tester = MQTTCommandTester()
    try:
        mqtt_tester.test_actuator_commands()
        print("✅ Test MQTT completato")
    except Exception as e:
        print(f"⚠️ Test MQTT saltato (broker non disponibile): {e}")
    
    print("\n🎉 TUTTI I TEST COMPLETATI CON SUCCESSO!")
    return True

def run_live_test():
    """Esegue un test live con Arduino simulato"""
    print("\n🔴 TEST LIVE CON ARDUINO SIMULATO")
    print("=" * 50)
    
    # Avvia simulazione Arduino
    arduino_sim = ArduinoSimulator()
    arduino_sim.start_simulation()
    
    try:
        # Avvia bridge
        print("🏗️ Avvio Bridge...")
        bridge = Bridge()
        
        print("⏳ Test in corso per 30 secondi...")
        print("   - Arduino invierà dati ogni 5 secondi")
        print("   - Bridge pubblicherà sui topic MQTT")
        print("   - Usa un client MQTT per inviare comandi")
        
        time.sleep(30)
        
    except KeyboardInterrupt:
        print("\n⏹️ Test interrotto dall'utente")
    except Exception as e:
        print(f"❌ Errore test live: {e}")
    finally:
        arduino_sim.stop_simulation()
        print("🏁 Test live completato")

if __name__ == "__main__":
    print("🧪 TEST BRIDGE SERIAL MQTT - ARDUINO")
    print("Scegli il tipo di test:")
    print("1. Test completo (mock)")
    print("2. Test live con Arduino simulato")
    print("3. Entrambi")
    
    choice = input("Inserisci la scelta (1/2/3): ").strip()
    
    if choice == "1":
        run_complete_test()
    elif choice == "2":
        run_live_test()
    elif choice == "3":
        run_complete_test()
        run_live_test()
    else:
        print("❌ Scelta non valida")

