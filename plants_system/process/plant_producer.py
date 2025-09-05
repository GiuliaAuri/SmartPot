import logging
import time
from conf.mqtt_conf_params import MqttConfigurationParameters
from plants_system.smart_objects.models.plant_descriptor import PlantDescriptor
import paho.mqtt.client as mqtt
from plants_system.smart_objects.models.Device import Device
from plants_system.smart_objects.models.Sensor import Sensor


class PlantProducer:
    def __init__(self, plant_descriptor: PlantDescriptor):
        self.plant_descriptor = plant_descriptor
        client_id = f"{self.plant_descriptor.plant_id}-plant-producer"
        self.client = mqtt.Client(client_id)
        self.client.on_connect = self.on_connect
        self.client.connect(MqttConfigurationParameters.BROKER_ADDRESS, MqttConfigurationParameters.BROKER_PORT)
        self.running = False

    def run(self):
        self.client.loop_start()
        self.publish_plant_info()
        self.running = True
        try:
            while self.running:
                self.generate_telemetry()
                time.sleep(10)
        finally:
            self.client.loop_stop()

    def stop(self):
        self.running = False
        self.client.loop_stop()
        self.client.disconnect()
        logging.info("PlantProducer stopped...")
        
    def on_connect(self, client, userdata, flags, rc):
        logging.info("Connected with result code %s", str(rc))

    def generate_telemetry(self):
        for device in self.plant_descriptor.devices:
            device.update_measurements()
            self.publish_telemetry_data()

    def publish_telemetry_data(self):
        for device in self.plant_descriptor.devices:
            for sensor in device.sensors:
                topic = MqttConfigurationParameters.build_telemetry_plant_topic(
                    self.plant_descriptor.plant_id, sensor.device, sensor.type
                )
                self.client.publish(topic, sensor.to_json())
                logging.info("Published telemetry: %s %s", topic, sensor.to_json())

    def publish_plant_info(self):
        topic = MqttConfigurationParameters.build_info_plant_topic(self.plant_descriptor.plant_id)
        self.client.publish(topic, self.plant_descriptor.to_json())
        logging.info("Published plant info: %s %s", topic, self.plant_descriptor.to_json())