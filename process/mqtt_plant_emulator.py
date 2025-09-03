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
from model.irrigation_actuator import IrrigationActuatorResource

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("producer")

class MqttPlantEmulator:
    def __init__(self):
        self.client = mqtt.Client()
        

    # The callback for when the client receives a CONNACK response from the server.
    def on_connect(client, userdata, flags, rc):
        logger.info("Connected with result code %s", str(rc))


    def publish_telemetry_data():
        target_topic = MqttConfigurationParameters.build_telemetry_plant_topic(
            plant_id, plant_descriptor.uuid, environment_telemetry.resource_id
        )
        device_payload_string = environment_telemetry.to_json()
        mqtt_client.publish(target_topic, device_payload_string, 0, False)
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

    #TODO da eliminare trasformando tutto in funzioni
    plant_id = match.group(1)  # plant_id
    # check topic
    match = re.match(MqttConfigurationParameters.build_command_plant_topic(plant_id, "+", "+"), topic)
    if not match:
        logger.warning("Message on unexpected topic: %s", topic)
        return

    # check payload
    try:
        data = json.loads(payload)
        command = data.get("command")
    except json.JSONDecodeError:
        command = payload.strip().upper()

    if command == "ON":
        IrrigationActuatorResource.changestatus(plant_id, True)
        logger.info("Relay simulated for %s: ON", plant_id)
    elif command == "OFF":
        IrrigationActuatorResource.changestatus(plant_id, False)
        logger.info("Relay simulated for %s: OFF", plant_id)
    else:
        logger.warning("Invalid command for %s: %s", plant_id, command)



# Configuration variables
plant_id = "python-plant-{0}".format(MqttConfigurationParameters.MQTT_USERNAME)
message_limit = 1000

mqtt_client = mqtt.Client(client_id=plant_id)
mqtt_client.on_connect = on_connect

# Set Account Username & Password
mqtt_client.username_pw_set(MqttConfigurationParameters.MQTT_USERNAME, MqttConfigurationParameters.MQTT_PASSWORD)

logger.info("Connecting to %s port: %s", MqttConfigurationParameters.BROKER_ADDRESS, str(MqttConfigurationParameters.BROKER_PORT))
mqtt_client.connect(MqttConfigurationParameters.BROKER_ADDRESS, MqttConfigurationParameters.BROKER_PORT)

# Start the MQTT sub - actuator
mqtt_client.on_message = on_message
command_topic = MqttConfigurationParameters.build_command_plant_topic(plant_id, "+", "+")
mqtt_client.subscribe(command_topic, qos=1)
logger.info("Subscribed to commands on %s", command_topic)

mqtt_client.loop_start()

# Create Plant Reference
plant_descriptor = PlantDescriptor(plant_id, "catus")

# Create the object to handle Plant Telemetry Data
environment_telemetry = EnvironmentTelemetryData()

publish_device_info()

try:
    for message_id in range(message_limit):
        environment_telemetry.update_measurements()
        publish_telemetry_data()
        time.sleep(3)
finally:
    mqtt_client.loop_stop()
    mqtt_client.disconnect()


mqtt_client.loop_stop()
