import paho.mqtt.client as mqtt
from conf.mqtt_conf_params import MqttConfigurationParameters
from data_collector.plant_descriptor import PlantDescriptor
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
        # Compatibilità con versioni vecchie e nuove di paho-mqtt
        try:
            self.client = mqtt.Client(mqtt.CallbackAPIVersion.VERSION1, client_id)
        except AttributeError:
            # Versione vecchia di paho-mqtt
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
        
        Converte i comandi in formato compatibile con il bridge.
        """
        # Converte comandi in formato semplice compatibile con bridge
        simple_command = self.convert_to_simple_command(command)
        
        if simple_command:
            # Usa il mapping degli attuatori del bridge
            actuator_type = "irrigation"  # Default per ora
            
            topic = MqttConfigurationParameters.build_command_plant_topic(actuator_type)
            self.client.publish(topic, simple_command)
            logging.info("Published command: %s to topic: %s", simple_command, topic)
    
    def convert_to_simple_command(self, command: str):
        """
        Converte comandi complessi in formato semplice per il bridge.
        
        Args:
            command: Comando complesso (es. "Activate irrigation", "Deactivate irrigation")
            
        Returns:
            str: Comando semplice (es. "start", "stop")
        """
        command_lower = command.lower()
        
        # Mapping comandi complessi -> semplici
        if "activate" in command_lower or "start" in command_lower or "on" in command_lower:
            return "start"
        elif "deactivate" in command_lower or "stop" in command_lower or "off" in command_lower:
            return "stop"
        else:
            # Se è già un comando semplice, restituiscilo
            if command_lower in ["start", "stop", "on", "off", "1", "0"]:
                return command_lower
            else:
                logging.warning(f"Unknown command format: {command}")
                return None
    
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

