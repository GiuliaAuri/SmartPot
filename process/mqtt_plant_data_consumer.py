import sys
import os
import logging
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
import paho.mqtt.client as mqtt
from conf.mqtt_conf_params import MqttConfigurationParameters

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("consumer")

# The callback for when the client receives a CONNACK response from the server.
def on_connect(client, userdata, flags, rc):
    logger.info("Connected with result code %s", str(rc))

    device_info_topic = MqttConfigurationParameters.build_info_plant_topic(
        plant_id
    )

    mqtt_client.subscribe(device_info_topic)

    logger.info("Subscribed to: %s", device_info_topic)

    device_telemetry_topic = MqttConfigurationParameters.build_telemetry_plant_topic(
        plant_id, "+", "+"
    )

    mqtt_client.subscribe(device_telemetry_topic)

    logger.info("Subscribed to: %s", device_telemetry_topic)


# Define a callback method to receive asynchronous messages
def on_message(client, userdata, message):
    message_payload = str(message.payload.decode("utf-8"))
    logger.info(f"Received IoT Message: Topic: {message.topic} Payload: {message_payload}")

# Configuration variables
plant_id = "python-plant-consumer-{0}".format(MqttConfigurationParameters.MQTT_USERNAME)
message_limit = 1000

mqtt_client = mqtt.Client(client_id=plant_id)
mqtt_client.on_message = on_message
mqtt_client.on_connect = on_connect

# Set Account Username & Password
mqtt_client.username_pw_set(MqttConfigurationParameters.MQTT_USERNAME, MqttConfigurationParameters.MQTT_PASSWORD)

logger.info("Connecting to %s port: %s", MqttConfigurationParameters.BROKER_ADDRESS, str(MqttConfigurationParameters.BROKER_PORT))
mqtt_client.connect(MqttConfigurationParameters.BROKER_ADDRESS, MqttConfigurationParameters.BROKER_PORT)

mqtt_client.loop_forever()
