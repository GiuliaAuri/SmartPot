import logging
import time
import paho.mqtt.client as mqtt
import json
import os
import asyncio
import threading
import concurrent.futures
from conf.mqtt_conf_params import MqttConfigurationParameters
from data_collector.plant_descriptor import PlantDescriptor
from data_collector.policy_manager import PolicyManager
from data_collector.data_collector_producer import DataCollectorProducer
from data_collector.json_manager import JsonManager

class DataCollectorConsumer:
    """
    Consumer MQTT semplificato per la raccolta e elaborazione dei dati delle piante.
    
    Questa versione è molto più semplice e leggibile:
    - Usa JsonManager per tutte le operazioni sui file JSON
    - Mantiene la logica MQTT interna
    - Mantiene la logica delle policy nel PolicyManager
    - Struttura più chiara e facile da leggere
    """
    
    def __init__(self, plant_descriptor: PlantDescriptor, path: str):
        
        self.plant_descriptor = plant_descriptor
        self.running = False
        
        # Inizializza JsonManager per il salvataggio dei dati
        self.json_manager = JsonManager(base_path=path)
        
        # Inizializza PolicyManager per la valutazione delle policy
        self.policy_manager = PolicyManager()

        # Configurazione MQTT
        client_id = f"{plant_descriptor.plant_id}-data-collector-consumer"
        try:
            self.client = mqtt.Client(mqtt.CallbackAPIVersion.VERSION1, client_id)
        except AttributeError:
            self.client = mqtt.Client(client_id)
        
        self.client.on_connect = self.on_connect
        self.client.on_message = self.on_message
        
    
    def on_connect(self, client, userdata, flags, rc):
        """Callback per la connessione MQTT."""
        logging.info("Connected with result code %s", str(rc))
        if rc == 0:
            # Sottoscriviti ai topic dei sensori
            
            for sensor in self.plant_descriptor.sensors:
                topic = MqttConfigurationParameters.build_telemetry_plant_topic(
                    sensor.type
                )
                self.client.subscribe(topic)
                print(f"🔔 Sottoscritto al topic: {topic}")
                logging.info(f"Subscribed to topic: {topic}")
    
    def on_message(self, client, userdata, msg):
        """
        Callback per la ricezione di messaggi MQTT.
        
        Gestisce payload semplici dal bridge (solo valore numerico) e li converte
        nel formato interno del sistema.
        """
        if not self.running:
            return
        
        try:
            message_payload = msg.payload.decode("utf-8")
            print(f"📨 Messaggio ricevuto - Topic: {msg.topic}, Payload: {message_payload}")
            logging.debug(f"Received message on topic {msg.topic}")
            
            # Estrai il tipo di sensore dal topic
            # Topic formato: plant/sensor/{sensor_type}
            topic_parts = msg.topic.split('/')
            sensor_type = topic_parts[-1] if len(topic_parts) >= 3 else "unknown"
            
            # Il bridge invia solo il valore numerico
            try:
                sensor_value = float(message_payload)
            except ValueError:
                logging.warning(f"Invalid sensor value: {message_payload}")
                return
            
            # Crea il messaggio nel formato interno
            message_data = {
                'topic': msg.topic,
                'payload': message_payload,
                'sensor_type': sensor_type,
                'value': sensor_value,
                'device_name': 'environment_telemetry',  # Default device
                'timestamp': int(time.time())
            }
            
            logging.info(f"Processed sensor data: {sensor_type} = {sensor_value}")
            
            # Processa i dati del sensore e valuta le policy tramite JsonManager
            actions = self.json_manager.process_sensor_data_and_evaluate_policies(
                plant_descriptor=self.plant_descriptor,
                sensor_type=sensor_type,
                sensor_value=sensor_value,
                policy_manager=self.policy_manager
            )
            
            # Esegui le azioni tramite il producer solo per activate/deactivate
            for action_str in actions:
                print(f"⚡ Esecuzione azione per {self.plant_descriptor.plant_id}: {action_str}")
                
                # Verifica se l'azione è activate o deactivate
                if "activate" in action_str.lower() or "deactivate" in action_str.lower():
                    try:
                        # Crea e avvia il producer per eseguire l'azione
                        producer = DataCollectorProducer(
                            plant_descriptor=self.plant_descriptor, 
                            command=action_str, 
                            json_path=self.json_manager.base_path
                        )
                        producer.run()
                        print(f"✅ Azione eseguita: {action_str}")
                    except Exception as e:
                        logging.error(f"Errore esecuzione azione {action_str}: {e}")
                else:
                    print(f"⚠️ Azione ignorata (non activate/deactivate): {action_str}")
            
        except Exception as e:
            logging.error(f"Error in on_message: {e}")
    
    def run(self):
        """
        Avvia il consumer MQTT e mantiene la connessione attiva.
        
        Questo metodo è molto più semplice e leggibile rispetto alla versione precedente.
        """
        print(f"🔧 Avvio DataCollectorConsumer per {self.plant_descriptor.plant_id}")
        
        try:
            # Avvia l'event loop asyncio in un thread separato
            def run_async_loop():
                print(f"🔄 Avvio event loop asyncio per {self.plant_descriptor.plant_id}")
                self.loop = asyncio.new_event_loop()
                asyncio.set_event_loop(self.loop)
                self.loop.run_forever()
            
            async_thread = threading.Thread(target=run_async_loop, daemon=True)
            async_thread.start()
            
            # Attendi che l'event loop sia pronto
            time.sleep(0.1)
            
            # Connetti al broker MQTT
            print(f"🔌 Connessione MQTT per {self.plant_descriptor.plant_id}...")
            self.client.connect(MqttConfigurationParameters.BROKER_ADDRESS, MqttConfigurationParameters.BROKER_PORT)
            self.client.loop_start()
            self.running = True
            print(f"✅ DataCollectorConsumer {self.plant_descriptor.plant_id} avviato correttamente")
            
        except Exception as e:
            print(f"❌ Errore avvio DataCollectorConsumer {self.plant_descriptor.plant_id}: {e}")
            raise
        
        
    def stop(self):
        """
        Interrompe il consumer MQTT e termina la connessione.
        
        Questo metodo è molto più semplice e gestisce solo la pulizia essenziale.
        """
        logging.info("Stopping DataCollectorConsumer...")
        self.running = False
        
        # Disconnetti MQTT
        try:
            self.client.disconnect()
        except Exception as e:
            logging.warning(f"Error disconnecting MQTT client: {e}")
        
     
