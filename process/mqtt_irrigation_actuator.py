from asyncio.log import logger
import uuid
import paho.mqtt.client as mqtt

from conf.mqtt_conf_params import MqttConfigurationParameters
from actuator.irrigation_actuator import IrrigationActuatorResource

class MqttIrrigationActuator:
    def __init__(self, resource_id: str):
        self.client = mqtt.Client(resource_id)
        self.resource_id = resource_id
        self.irrigation_actuator = IrrigationActuatorResource("irrigation"+str(uuid.uuid4()))
        self.client.on_connect = self.on_connect
        self.client.on_message = self.on_message
        self.client.connect(MqttConfigurationParameters.BROKER_ADDRESS, MqttConfigurationParameters.BROKER_PORT)
        self.client.loop_start()

    def on_connect(self, client, userdata, flags, rc):
        logger.info("Connected with result code %s", str(rc))
        client.subscribe(MqttConfigurationParameters.build_command_plant_topic(self.resource_id, "+", "+"))

    def on_message(self, client, userdata, message):
        payload = message.payload.decode("utf-8")
        logger.info(f"Received IoT Message: Topic: {message.topic} Payload: {payload}")
        if payload.strip().upper() == "ON":
            self.irrigation_actuator.changestatus(self.resource_id, True)
            logger.info(f"Irrigation ON command received for resource {self.resource_id}")
        elif payload.strip().upper() == "OFF":
            self.irrigation_actuator.changestatus(self.resource_id, False)
            logger.info(f"Irrigation OFF command received for resource {self.resource_id}")
        else:
            logger.warning(f"Unknown command received: {payload}")
    
    def stop(self):
        self.client.loop_stop()
        self.client.disconnect()