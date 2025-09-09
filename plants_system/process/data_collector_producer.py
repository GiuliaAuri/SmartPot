import paho.mqtt.client as mqtt
from conf.mqtt_conf_params import MqttConfigurationParameters
from plants_system.smart_objects.models.plant_descriptor import PlantDescriptor
import logging
import time

class DataCollectorProducer:
    """
    Producer MQTT per l'invio di comandi agli attuatori delle piante.
    
    Questa classe gestisce la pubblicazione di comandi MQTT agli attuatori
    delle piante, permettendo al sistema di controllare dispositivi come
    l'irrigazione automatica basandosi sulle policy valutate.
    """
    def __init__(self, plant_descriptor: PlantDescriptor, command:str):
        self.plant_descriptor = plant_descriptor
        self.command=command
        client_id = f"{self.plant_descriptor.plant_id}-data-collector-producer"
        self.client = mqtt.Client(client_id)
        self.client.on_connect = self.on_connect
        self.running = True
        
    
    def on_connect(self, client, userdata, flags, rc):
        """
        Callback per la connessione MQTT.
        
        Questo metodo viene chiamato quando il producer si connette al broker MQTT.
        """
        logging.info("Connected with result code %s", str(rc))
    
    def publish_command(self, command: str):
        """
        Pubblica un comando MQTT agli attuatori delle piante.
        
        Questo metodo pubblica un comando MQTT agli attuatori delle piante.
        """
        for device in self.plant_descriptor.devices:
            for actuator in device.actuators:
                topic=MqttConfigurationParameters.build_command_plant_topic(self.plant_descriptor.plant_id,device.device)
                self.client.publish(topic, command)
                logging.info("Published command: %s to topic: %s", command, topic)
    
    def run(self):
        """
        Avvia il producer MQTT e pubblica il comando.
        
        Questo metodo si connette al broker MQTT, pubblica il comando e termina il loop.
        """
        self.client.connect(MqttConfigurationParameters.BROKER_ADDRESS, MqttConfigurationParameters.BROKER_PORT)
        self.client.loop_start() 
        self.publish_command(self.command)
        time.sleep(2) 
        self.client.loop_stop()

