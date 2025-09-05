import time
from conf.mqtt_conf_params import MqttConfigurationParameters
import logging
import paho.mqtt.client as mqtt
from plants_system.smart_objects.models.plant_descriptor import PlantDescriptor
from plants_system.smart_objects.models.Device import Device
from plants_system.smart_objects.models.SwitchActuator import SwitchActuator

class PlantConsumer():
    def __init__(self, plant_descriptor: PlantDescriptor):
        self.plant_descriptor = plant_descriptor
        client_id = f"{self.plant_descriptor.plant_id}-plant-consumer"
        self.client = mqtt.Client(client_id)
        self.client.on_connect = self.on_connect
        self.client.on_message = self.on_message
        self.running = False

    def run(self):
        self.client.connect(MqttConfigurationParameters.BROKER_ADDRESS, MqttConfigurationParameters.BROKER_PORT)
        self.client.loop_start()
        self.running = True
        try:
            while self.running:
                time.sleep(1)  
        finally:
            self.client.loop_stop()

    def stop(self):
        self.running = False
        self.client.disconnect()
        logging.info("PlantConsumer stopped...")

    def on_connect(self, client, userdata, flags, rc):
        for device in self.plant_descriptor.devices:
            for actuator in device.actuators:
                plant_topic = MqttConfigurationParameters.build_command_plant_topic(self.plant_descriptor.plant_id, device.device)
                self.client.subscribe(plant_topic)
                logging.info(f"Subscribed to topic: {plant_topic}")

    def on_message(self, client, userdata, msg):
        message_payload = str(msg.payload.decode("utf-8"))
        logging.info(f"Received message: {message_payload}")
        #TODO cambiare lo stato dell'attuatore - qui solo uno ce nè
        for device in self.plant_descriptor.devices:
            for actuator in device.actuators:
                actuator.handle_command(command=message_payload)





