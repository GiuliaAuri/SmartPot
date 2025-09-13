import logging
import time
from conf.mqtt_conf_params import MqttConfigurationParameters
from plants_system.smart_objects.models.plant_descriptor import PlantDescriptor
import paho.mqtt.client as mqtt
from plants_system.smart_objects.models.Device import Device
from plants_system.smart_objects.models.Sensor import Sensor


class PlantProducer:
    """
    Producer MQTT per la pubblicazione dei dati telemetrici delle piante.
    
    Questa classe gestisce la pubblicazione dei dati telemetrici delle piante
    attraverso MQTT, inclusi dati provenienti dai sensori e informazioni
    di base sulla pianta.
    """
    def __init__(self, plant_descriptor: PlantDescriptor):
        self.plant_descriptor = plant_descriptor
        client_id = f"{self.plant_descriptor.plant_id}-plant-producer"
        # Compatibilità con versioni vecchie e nuove di paho-mqtt
        try:
            self.client = mqtt.Client(mqtt.CallbackAPIVersion.VERSION1, client_id)
        except AttributeError:
            # Versione vecchia di paho-mqtt
            self.client = mqtt.Client(client_id)
        self.client.on_connect = self.on_connect
        self.client.connect(MqttConfigurationParameters.BROKER_ADDRESS, MqttConfigurationParameters.BROKER_PORT)
        self.running = False

    def run(self):
        """
        Avvia il producer MQTT e pubblica i dati telemetrici e informazioni sulla pianta.
        
        Si connette al broker MQTT, pubblica i dati telemetrici e informazioni sulla pianta
        e rimane in esecuzione fino a quando non viene chiamato stop().
        """
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
        """
        Interrompe il producer MQTT e termina la connessione.
        
        Questo metodo chiude il loop di pubblicazione e si disconnette dal broker MQTT.
        """
        self.running = False
        self.client.loop_stop()
        self.client.disconnect()
        logging.info("PlantProducer stopped...")
        
    def on_connect(self, client, userdata, flags, rc):
        """
        Callback per la connessione MQTT.
        
        Questo metodo viene chiamato quando il producer si connette al broker MQTT.
        """
        logging.info("Connected with result code %s", str(rc))

    def generate_telemetry(self):
        """
        Genera i dati telemetrici per tutti i dispositivi della pianta.
        
        Questo metodo aggiorna le misurazioni di tutti i dispositivi della pianta
        e pubblica i dati telemetrici.
        """
        for device in self.plant_descriptor.devices:
            device.update_measurements()
        # Pubblica una sola volta dopo aver aggiornato tutti i dispositivi
        self.publish_telemetry_data()

    def publish_telemetry_data(self):
        """
        Pubblica i dati telemetrici per tutti i sensori della pianta.
        
        Questo metodo pubblica i dati telemetrici per tutti i sensori della pianta,
        evitando pubblicazioni duplicate.
        """
        published_sensors = set()  # Evita pubblicazioni duplicate
        for device in self.plant_descriptor.devices:
            for sensor in device.sensors:
                sensor_key = f"{sensor.device}_{sensor.type}"
                if sensor_key not in published_sensors:
                    topic = MqttConfigurationParameters.build_telemetry_plant_topic(
                        self.plant_descriptor.plant_id, sensor.device, sensor.type
                    )
                    self.client.publish(topic, sensor.to_json())
                    logging.info("Published telemetry: %s %s", topic, sensor.to_json())
                    published_sensors.add(sensor_key)

    def publish_plant_info(self):
        """
        Pubblica le informazioni sulla pianta.
        
        Questo metodo pubblica le informazioni sulla pianta, incluse le misurazioni
        dei sensori e le informazioni di base sulla pianta.
        """
        topic = MqttConfigurationParameters.build_info_plant_topic(self.plant_descriptor.plant_id)
        self.client.publish(topic, self.plant_descriptor.to_json(), qos=1, retain=True)
        logging.info("Published plant info: %s %s", topic, self.plant_descriptor.to_json())