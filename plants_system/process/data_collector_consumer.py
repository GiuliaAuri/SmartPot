import logging
import time
import paho.mqtt.client as mqtt
import json
from conf.mqtt_conf_params import MqttConfigurationParameters
from plants_system.smart_objects.models.plant_descriptor import PlantDescriptor
from plants_system.process.policy_manager import PolicyManager
from plants_system.process.data_collector_producer import DataCollectorProducer

class DataCollectorConsumer:
    def __init__(self, plant_descriptor: PlantDescriptor):
        self.plant_descriptor = plant_descriptor
        client_id = f"{self.plant_descriptor.plant_id}-data-collector-consumer"
        self.client = mqtt.Client(client_id)
        self.client.on_connect = self.on_connect
        self.client.on_message = self.on_message
        self.policy_manager = PolicyManager("plants_system/smart_objects/resources/policies_conf.json")
        self.running = False
 

    def on_connect(self, client, userdata, flags, rc):
       #TODO aggiungere sottoscrizione al topic info
       for device in self.plant_descriptor.devices:
           for sensor in device.sensors:
                topic = MqttConfigurationParameters.build_telemetry_plant_topic(
                    self.plant_descriptor.plant_id, sensor.device, sensor.type
                )
                self.client.subscribe(topic)
                print(f"Subscribed to topic: {topic}")
        
    

    def on_message(self, client, userdata, msg):
        message_payload = msg.payload.decode("utf-8")
        logging.info(f"Received message on topic {msg.topic}: {message_payload}")

        try:
            data = json.loads(message_payload)
            sensor_type = data.get("type")
            value = data.get("value")
            device_name = data.get("device")

            # aggiorna il sensore corrispondente nel plant_descriptor
            for device in self.plant_descriptor.devices:
                if device.device == device_name:
                    for sensor in device.sensors:
                        if sensor.type == sensor_type:
                            sensor.value = value
                            logging.debug(f"Updated sensor {sensor.type} of {device.device} to {sensor.value}")
                            break

        except Exception as e:
            logging.error(f"Error parsing message: {e}")

        self.policy_manager.evaluate(self.plant_descriptor)
        alerts = self.policy_manager.alerts.get(self.plant_descriptor.plant_id, [])
        for alert in alerts:
            print(f"ALERT: {alert}")
        actions=self.policy_manager.actions.get(self.plant_descriptor.plant_id, [])
        for action in actions:
            print(f"ACTION: {action}")
            data_collector_producer = DataCollectorProducer(self.plant_descriptor, action)
            data_collector_producer.run()

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
        logging.info("DataCollectorConsumer stopped...")
