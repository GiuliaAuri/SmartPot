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
    Consumer MQTT per la raccolta e elaborazione dei dati delle piante.
    """
    
    def __init__(self, plant_descriptor: PlantDescriptor, path: str):
        
        self.plant_descriptor = plant_descriptor
        self.running = False
        
        self.json_manager = JsonManager(base_path=path)
        
        self.policy_manager = PolicyManager()

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
            
            # Topic formato: plant/sensor/{sensor_type}
            topic_parts = msg.topic.split('/')
            sensor_type = topic_parts[-1] if len(topic_parts) >= 3 else "unknown"
            
            try:
                sensor_value = float(message_payload)
            except ValueError:
                logging.warning(f"Invalid sensor value: {message_payload}")
                return

            if sensor_type == "humidity":
                humidity_sensor = None
                for sensor in self.plant_descriptor.sensors:
                    if sensor.type == "humidity":
                        humidity_sensor = sensor
                        break
                
                if humidity_sensor:
                    sensor_value = humidity_sensor.calculate_relative_percentage(sensor_value)
            
            message_data = {
                'topic': msg.topic,
                'payload': message_payload,
                'sensor_type': sensor_type,
                'value': sensor_value,
                'device_name': 'environment_telemetry',
                'timestamp': int(time.time())
            }
            
            logging.info(f"Processed sensor data: {sensor_type} = {sensor_value}")
            
            actions = self.json_manager.process_sensor_data_and_evaluate_policies(
                plant_descriptor=self.plant_descriptor,
                sensor_type=sensor_type,
                sensor_value=sensor_value,
                policy_manager=self.policy_manager
            )
            
            for action_str in actions:
                print(f"⚡ Esecuzione azione per {self.plant_descriptor.plant_id}: {action_str}")
                
                if "activate" in action_str.lower() or "deactivate" in action_str.lower():
                    try:
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
        
        """
        print(f"🔧 Avvio DataCollectorConsumer per {self.plant_descriptor.plant_id}")
        
        try:
            def run_async_loop():
                print(f"🔄 Avvio event loop asyncio per {self.plant_descriptor.plant_id}")
                self.loop = asyncio.new_event_loop()
                asyncio.set_event_loop(self.loop)
                self.loop.run_forever()
            
            async_thread = threading.Thread(target=run_async_loop, daemon=True)
            async_thread.start()
            
            time.sleep(0.1) # attesa per la sincronizzazione dei thread
            
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
        
        """
        logging.info("Stopping DataCollectorConsumer...")
        self.running = False
        
        try:
            self.client.disconnect()
        except Exception as e:
            logging.warning(f"Error disconnecting MQTT client: {e}")
        
     
