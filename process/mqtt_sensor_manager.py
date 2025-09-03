import paho.mqtt.client as mqtt
import logging

from conf.mqtt_conf_params import MqttConfigurationParameters
from model.plant_descriptor import PlantDescriptor

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("sensor")

class MqttSensorManager:
    def __init__(self, plant_descriptor: PlantDescriptor):
        self.client = mqtt.Client(client_id=plant_descriptor.plant_id)
        self.plant_descriptor = plant_descriptor
        self.client.on_connect = self.on_connect
        self.client.on_message = self.on_message
        self.client.username_pw_set(MqttConfigurationParameters.MQTT_USERNAME, MqttConfigurationParameters.MQTT_PASSWORD)
        self.client.connect(MqttConfigurationParameters.BROKER_ADDRESS, MqttConfigurationParameters.BROKER_PORT)
        self.client.loop_start()

    def on_connect(self, client, userdata, flags, rc):
        logger.info("Connected with result code %s", str(rc))
        # Subscribe to telemetry info if you want to consume data from other sensors
        telemetry_topic = MqttConfigurationParameters.build_telemetry_plant_topic(self.plant_descriptor.plant_id, "+", "+")
        client.subscribe(telemetry_topic)
        logger.info("Subscribed to telemetry topic: %s", telemetry_topic)

    def on_message(self, client, userdata, message):
        payload = message.payload.decode("utf-8")
        logger.info(f"Received telemetry: Topic: {message.topic} Payload: {payload}")

    def publish_telemetry(self):
        for sensor in self.plant_descriptor.sensors:
            sensor.update()
            topic = MqttConfigurationParameters.build_telemetry_plant_topic(
                self.plant_descriptor.plant_id, sensor.device, sensor.type)
            self.client.publish(topic, sensor.to_json())
            logger.info("Published telemetry: %s %s", topic, sensor.to_json())

    def stop(self):
        self.client.loop_stop()
        self.client.disconnect()

# Esempio di utilizzo:
# sensor_manager = MqttSensorManager("plant01", "cactus")
# while True:
#     sensor_manager.publish_telemetry()
#     time.sleep(3)