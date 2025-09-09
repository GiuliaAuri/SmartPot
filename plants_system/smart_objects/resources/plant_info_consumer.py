import logging
from flask import json
import paho.mqtt.client as mqtt
import os
import json
from conf.mqtt_conf_params import MqttConfigurationParameters

class PlantInfoConsumer:
    """
    Consumer MQTT per la ricezione delle informazioni sulla pianta.
    
    Questa classe gestisce la ricezione delle informazioni sulla pianta
    attraverso MQTT, inclusi dati provenienti dai sensori e informazioni
    di base sulla pianta.
    """
    def __init__(self, filename):
        client_id = "plant-info-consumer"
        self.client = mqtt.Client(client_id)
        self.filename = filename
        self.running = True
        
    def on_connect(self, client, userdata, flags, rc):
        """
        Callback per la connessione MQTT.
        
        Questo metodo viene chiamato quando il consumer si connette al broker MQTT.
        """
        topic=MqttConfigurationParameters.build_info_plant_topic("+")
        self.client.subscribe(topic)
        logging.info(f"Subscribed to topic: {topic}")

    def on_message(self, client, userdata, msg):
        """
        Callback per la ricezione di messaggi MQTT.
        
        Questo metodo viene chiamato quando il consumer riceve un messaggio MQTT.
        """
        logging.info(f"Received message on topic {msg.topic}: {msg.payload.decode('utf-8')}")
        # Decodifica il messaggio ricevuto come JSON
        try:
            payload = json.loads(msg.payload.decode('utf-8'))
        except Exception as e:
            logging.error(f"Errore nel parsing del messaggio: {e}")
            return

        # Se il file non esiste, crea una lista vuota
        if not os.path.exists(self.filename):
            plants = []
        else:
            with open(self.filename, "r") as f:
                try:
                    plants = json.load(f)
                except Exception:
                    plants = []

        # Aggiorna o aggiungi la pianta
        updated = False
        for i, p in enumerate(plants):
            if p.get("plant_id") == payload.get("plant_id"):
                plants[i] = payload
                updated = True
                break
        if not updated:
            plants.append(payload)

        # Salva la lista aggiornata nel file
        with open(self.filename, "w") as f:
            json.dump(plants, f, indent=2)
        logging.info(f"Saved/updated plant {payload.get('plant_id')} into {self.filename}")

    def run(self):
        """
        Avvia il consumer MQTT e mantiene la connessione attiva.
        
        Si connette al broker MQTT e inizia il loop di ricezione messaggi.
        Il metodo rimane in esecuzione fino a quando non viene chiamato stop().
        """
        self.client.on_connect = self.on_connect
        self.client.on_message = self.on_message
        self.client.connect(MqttConfigurationParameters.BROKER_ADDRESS, MqttConfigurationParameters.BROKER_PORT)
        self.client.loop_start()

    def stop(self):
        """
        Interrompe il consumer MQTT e termina la connessione.
        
        Questo metodo chiude il loop di ricezione messaggi e si disconnette dal broker MQTT.
        """
        self.running = False
        self.client.loop_stop()
        self.client.disconnect()
        logging.info("PlantInfoConsumer stopped...")