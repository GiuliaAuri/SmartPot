import uuid
import paho.mqtt.client as mqtt
import logging
from conf.mqtt_conf_params import MqttConfigurationParameters
from plants_system.smart_objects.models.SwitchActuator import SwitchActuator
from plants_system.smart_objects.models.plant_descriptor import PlantDescriptor

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("actuator")

class MqttActuatorManager:
    def __init__(self, plant_descriptor: PlantDescriptor):
        self.client = mqtt.Client(client_id=f"{plant_descriptor.plant_id}-actuator-{uuid.uuid4()}")
        self.plant_descriptor = plant_descriptor
        self.client.on_connect = self.on_connect
        self.client.on_message = self.on_message
        self.client.on_disconnect = self.on_disconnect
        #self.client.username_pw_set(MqttConfigurationParameters.MQTT_USERNAME, MqttConfigurationParameters.MQTT_PASSWORD)
        self.client.connect(MqttConfigurationParameters.BROKER_ADDRESS, MqttConfigurationParameters.BROKER_PORT)
        self.client.loop_start()

    def on_connect(self, client, userdata, flags, rc):
        logger.info("Connected with result code %s", str(rc))
        for actuator in self.plant_descriptor.actuators:
            topic = MqttConfigurationParameters.build_command_plant_topic(
                self.plant_descriptor.plant_id, actuator.device
            )
            client.subscribe(topic)
            logger.info("Subscribed to command topic: %s", topic)

    def on_message(self, client, userdata, message):
        payload = message.payload.decode("utf-8")
        topic = message.topic
        # Identifica l'attuatore dal topic e aggiorna lo stato
        for actuator in self.plant_descriptor.actuators:
            expected_topic = MqttConfigurationParameters.build_command_plant_topic(
                self.plant_descriptor.plant_id, actuator.device
            )
            if topic == expected_topic:
                actuator.handle_command(payload)

    def send_command(self, command:str, actuator:SwitchActuator):
        topic = MqttConfigurationParameters.build_command_plant_topic(self.plant_descriptor.plant_id, actuator.device)
        self.client.publish(topic, command)
        logger.info(f"Sent command: {command} to {topic}")

    def stop(self):
        self.client.loop_stop()
        self.client.disconnect()
    
    def on_disconnect(self, client, userdata, rc):
        logger.warning(f"Disconnected from MQTT broker with result code {rc}")

# Esempio di utilizzo:
# actuator_manager = MqttActuatorManager("irrigation01")
# actuator_manager.send_command("ON")