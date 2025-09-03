import sys
import os
import logging
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
import paho.mqtt.client as mqtt
import time
from model.plant_descriptor import PlantDescriptor
from device.environment_telemetry import EnvironmentTelemetryData
from conf.mqtt_conf_params import MqttConfigurationParameters
import re
import json

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("producer")

class MqttSensor:
    def __init__(self, plant_id:str, species:str):
        self.client = mqtt.Client()
        self.environment_telemetry = EnvironmentTelemetryData(plant_id)
        self.plant_descriptor = PlantDescriptor(plant_id, species)


    # The callback for when the client receives a CONNACK response from the server.
    def on_connect(client, userdata, flags, rc):
        logger.info("Connected with result code %s", str(rc))


    def publish_telemetry_data(self):
        target_topic = MqttConfigurationParameters.build_telemetry_plant_topic(
            self.plant_descriptor.plant_id, self.environment_telemetry.resource self.environment_telemetry.resource_id
        )
        device_payload_string = self.environment_telemetry.to_json()
        self.client.publish(target_topic, device_payload_string, 0, False)
        logger.info("Telemetry Data Published: Topic: %s Payload: %s", target_topic, device_payload_string)


    def publish_device_info():
        target_topic = MqttConfigurationParameters.build_info_plant_topic(plant_id)
        device_payload_string = plant_descriptor.to_json()
        mqtt_client.publish(target_topic, device_payload_string, 0, True)
        logger.info("Plant Info Published: Topic: %s Payload: %s", target_topic, device_payload_string)

    def on_message(client, userdata, message):
        topic = message.topic
        payload = message.payload.decode("utf-8")
        logger.info(f"Received IoT Message: Topic: {topic} Payload: {payload}")


