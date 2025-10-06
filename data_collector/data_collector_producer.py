import paho.mqtt.client as mqtt
from conf.mqtt_conf_params import MqttConfigurationParameters
from data_collector.plant_descriptor import PlantDescriptor
from data_collector.json_manager import JsonManager
import logging
import time

class DataCollectorProducer:
    """
    Producer MQTT per l'invio di comandi agli attuatori delle piante.

    """
    def __init__(self, plant_descriptor: PlantDescriptor, command: str, json_path: str = "cloud_simulator/plants_log"):
        self.plant_descriptor = plant_descriptor
        self.command = command
        
        self.json_manager = JsonManager(base_path=json_path)
        
        client_id = f"{self.plant_descriptor.plant_id}-data-collector-producer"
        try:
            self.client = mqtt.Client(mqtt.CallbackAPIVersion.VERSION1, client_id)
        except AttributeError:
            self.client = mqtt.Client(client_id)
        self.client.on_connect = self.on_connect
        self.running = True
        
    
    def on_connect(self, client, userdata, flags, rc):
        """
        Callback per la connessione MQTT.
        
        """
        logging.info("Connected with result code %s", str(rc))
    
    def publish_command(self, command: str):
        """
        Pubblica un comando MQTT agli attuatori delle piante.
        
        """
        simple_command = self.convert_to_simple_command(command)
        
        if simple_command:
            actuator_type = "irrigation"  # Default per ora
            
            topic = MqttConfigurationParameters.build_command_plant_topic(actuator_type)
            self.client.publish(topic, simple_command)
            logging.info("Published command: %s to topic: %s", simple_command, topic)
            
            self.save_actuator_action(actuator_type, simple_command)
    
    def save_actuator_action(self, actuator_type: str, action: str):
        """
        Salva l'azione di un attuatore nel file JSON.
        
        Args:
            actuator_type: Tipo di attuatore (es. "irrigation")
            action: Azione eseguita (es. "start", "stop")
        """
        try:
            self.json_manager.save_actuator_data(
                plant_id=self.plant_descriptor.plant_id,
                actuator_type=actuator_type,
                action=action,
                species=self.plant_descriptor.species
            )
            print(f"💾 Azione attuatore salvata: {actuator_type} = {action}")
        except Exception as e:
            logging.error(f"Errore salvataggio attuatore {actuator_type}: {e}")
    
    def convert_to_simple_command(self, command: str):
        """
        Converte comandi complessi in formato semplice per il bridge.
        
        Args:
            command: Comando complesso (es. "Activate irrigation", "Deactivate irrigation")
            
        Returns:
            str: Comando semplice (es. "start", "stop")
        """
        command_lower = command.lower()
        
        if "deactivate" in command_lower or "stop" in command_lower or "off" in command_lower:
            return "stop"
        elif "activate" in command_lower or "start" in command_lower or "on" in command_lower:
            return "start"
        else:
            if command_lower in ["start", "stop", "on", "off", "1", "0"]:
                return command_lower
            else:
                logging.warning(f"Unknown command format: {command}")
                return None
    
    def run(self):
        """
        Avvia il producer MQTT e pubblica il comando.
        
        """
        self.client.connect(MqttConfigurationParameters.BROKER_ADDRESS, MqttConfigurationParameters.BROKER_PORT)
        self.client.loop_start() 
        self.publish_command(self.command)
        time.sleep(2) 
        self.client.loop_stop()

