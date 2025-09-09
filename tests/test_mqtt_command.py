#!/usr/bin/env python3
"""
Script per testare comandi MQTT agli attuatori delle piante
"""
import paho.mqtt.client as mqtt
import time
import sys

def test_mqtt_command(plant_id, device_id, command):
    """
    Testa l'invio di un comando MQTT a un attuatore
    
    Args:
        plant_id (str): ID della pianta (es. 'my_cactus1')
        device_id (str): ID del dispositivo (es. 'water_metering')
        command (str): Comando da inviare (es. 'Activate irrigation')
    """
    # Crea il topic
    topic = f"plant/{plant_id}/device/{device_id}/command"
    
    # Crea client MQTT
    client = mqtt.Client(f"test-{plant_id}-command")
    
    def on_connect(client, userdata, flags, rc):
        print(f"Connesso al broker MQTT con codice: {rc}")
        if rc == 0:
            print(f"Inviando comando '{command}' al topic: {topic}")
            client.publish(topic, command)
            print("Comando inviato!")
        else:
            print(f"Errore di connessione: {rc}")
    
    def on_publish(client, userdata, mid):
        print(f"Messaggio pubblicato con ID: {mid}")
        client.disconnect()
    
    # Configura callback
    client.on_connect = on_connect
    client.on_publish = on_publish
    
    try:
        # Connetti al broker
        client.connect("localhost", 1883, 60)
        client.loop_start()
        
        # Aspetta un po' per completare l'operazione
        time.sleep(2)
        
    except Exception as e:
        print(f"Errore: {e}")
    finally:
        client.loop_stop()
        client.disconnect()

if __name__ == "__main__":
    if len(sys.argv) != 4:
        print("Uso: python test_mqtt_command.py <plant_id> <device_id> <command>")
        print("Esempio: python test_mqtt_command.py my_cactus1 water_metering 'Activate irrigation'")
        sys.exit(1)
    
    plant_id = sys.argv[1]
    device_id = sys.argv[2]
    command = sys.argv[3]
    
    print(f"Test comando MQTT:")
    print(f"  Pianta: {plant_id}")
    print(f"  Dispositivo: {device_id}")
    print(f"  Comando: {command}")
    print("-" * 50)
    
    test_mqtt_command(plant_id, device_id, command)
