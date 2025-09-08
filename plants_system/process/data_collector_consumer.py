import logging
import time
import paho.mqtt.client as mqtt
import json
import os
from conf.mqtt_conf_params import MqttConfigurationParameters
from plants_system.smart_objects.models.plant_descriptor import PlantDescriptor
from plants_system.process.policy_manager import PolicyManager
from plants_system.process.data_collector_producer import DataCollectorProducer

class DataCollectorConsumer:
    def __init__(self, plant_descriptor: PlantDescriptor, path:str):
        self.plant_descriptor = plant_descriptor
        self.filename=path+self.plant_descriptor.plant_id+".json"
        client_id = f"{self.plant_descriptor.plant_id}-data-collector-consumer"
        self.client = mqtt.Client(client_id)
        self.client.on_connect = self.on_connect
        self.client.on_message = self.on_message
        self.policy_manager = PolicyManager("plants_system/smart_objects/resources/policies_conf.json")
        self.running = False
 
    def on_connect(self, client, userdata, flags, rc):
        logging.info("Connected with result code %s", str(rc))
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

            # Aggiorna la storia del sensore nel file json
            self.update_sensor_history(sensor_type, value, device_name)

        except Exception as e:
            logging.error(f"Error parsing message: {e}")

        # Rivaluta le policy
        logging.info(f"Evaluating policies for plant {self.plant_descriptor.plant_id}")
        self.policy_manager.evaluate(self.plant_descriptor)
        alerts = self.policy_manager.alerts.get(self.plant_descriptor.plant_id, [])
        actions = self.policy_manager.actions.get(self.plant_descriptor.plant_id, [])
        
        logging.info(f"Plant {self.plant_descriptor.plant_id} - Alerts: {len(alerts)}, Actions: {len(actions)}")
        for alert in alerts:
            print(f"ALERT: {alert}")
            logging.info(f"ALERT: {alert}")
        
        # Salva gli alert nei file JSON
        if alerts:
            logging.info(f"Saving {len(alerts)} alerts to JSON file")
            self.update_alerts_history(alerts)
        else:
            logging.debug(f"No alerts to save for plant {self.plant_descriptor.plant_id}")

        # Esegui solo le azioni relative al sensore appena aggiornato
        actions = self.policy_manager.actions.get(self.plant_descriptor.plant_id, [])
        for action in actions:
            action_parts = action.split()
            if len(action_parts) < 2:
                continue
            actuator_type = action_parts[1]
            desired_value = True if action_parts[0].lower() == "activate" else False

            # Cerca la policy corrispondente
            for policy in self.policy_manager.plant_policies.get(self.plant_descriptor.plant_id, []):
                if (
                    policy.get("action", "").capitalize() + " " + policy.get("actuator", "") == action
                    and policy.get("sensor", "") == sensor_type
                ):
                    # Trova l'attuatore
                    for device in self.plant_descriptor.devices:
                        for actuator in getattr(device, "actuators", []):
                            if getattr(actuator, "type", None) == actuator_type:
                                # Solo se lo stato deve cambiare
                                if getattr(actuator, "status", None) != desired_value:
                                    print(f"ACTION: {action}")
                                    self.update_actuator_history(action)
                                    data_collector_producer = DataCollectorProducer(self.plant_descriptor, action)
                                    data_collector_producer.run()
                                else:
                                    logging.info(f"No ACTION: {action} (actuator already in desired state)")
                                break
                    break  # esegui solo una volta per questa azione
            
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


    def update_sensor_history(self, sensor_type, value, device_name):
        timestamp = int(time.time())
        # Se il file non esiste, crea la struttura base
        if not os.path.exists(self.filename):
            plants = [{
                "plant_id": self.plant_descriptor.plant_id,
                "sensors": [],
                "actuators": []
            }]
        else:
            with open(self.filename, "r") as f:
                plants = json.load(f)

        for plant in plants:
            if plant["plant_id"] == self.plant_descriptor.plant_id:
                found = False
                for s in plant["sensors"]:
                    if s.get("sensor") == sensor_type and s.get("device") == device_name:
                        found = True
                        if "values" not in s:
                            s["values"] = []
                        # Solo memorizzare se il valore è cambiato
                        if not s["values"] or s["values"][-1]["value"] != value:
                            s["values"].append({"value": value, "timestamp": str(timestamp)})
                            logging.info(f"Stored new sensor value: {sensor_type} = {value}")
                        else:
                            logging.debug(f"Skipped duplicate sensor value: {sensor_type} = {value}")
                        break
                if not found:
                    plant["sensors"].append({
                        "sensor": sensor_type,
                        "device": device_name,
                        "values": [{"value": value, "timestamp": str(timestamp)}]
                    })
                break

        with open(self.filename, "w") as f:
            json.dump(plants, f, indent=2)

    #TODO da aggiungere alla chiamata
    def update_actuator_history(self, action):
        timestamp = int(time.time())
        action_parts = action.split()
        if len(action_parts) < 2:
            logging.warning(f"Cannot parse action: {action}")
            return

        action_type = action_parts[0]  # "Activate" o "Deactivate"
        actuator_type = action_parts[1]  # nome attuatore (es: "irrigation")

        value = True if action_type.lower() == "activate" else False

        # Cerca il device che contiene l'attuatore richiesto
        device_name = None
        for device in self.plant_descriptor.devices:
            for actuator in getattr(device, "actuators", []):
                if getattr(actuator, "type", None) == actuator_type:
                    device_name = device.device  # <-- usa il nome del device!
                    break
            if device_name:
                break

        if device_name is None:
            device_name = actuator_type  # fallback

        # Carica o crea il file
        if not os.path.exists(self.filename):
            plants = [{
                "plant_id": self.plant_descriptor.plant_id,
                "sensors": [],
                "actuators": []
            }]
        else:
            with open(self.filename, "r") as f:
                plants = json.load(f)

        for plant in plants:
            if plant["plant_id"] == self.plant_descriptor.plant_id:
                found = False
                for a in plant["actuators"]:
                    if a.get("actuator") == actuator_type and a.get("device") == device_name:
                        found = True
                        if "values" not in a:
                            a["values"] = []
                        # Solo memorizzare se il valore è cambiato
                        if not a["values"] or a["values"][-1]["value"] != value:
                            a["values"].append({"value": value, "timestamp": str(timestamp)})
                            logging.info(f"Stored new actuator value: {actuator_type} = {value}")
                        else:
                            logging.debug(f"Skipped duplicate actuator value: {actuator_type} = {value}")
                        break
                if not found:
                    plant["actuators"].append({
                        "actuator": actuator_type,
                        "device": device_name,
                        "values": [{"value": value, "timestamp": str(timestamp)}]
                    })
                break

        with open(self.filename, "w") as f:
            json.dump(plants, f, indent=2)

    def update_alerts_history(self, alerts):
        """Salva gli alert nei file JSON"""
        timestamp = int(time.time())
        
        # Se il file non esiste, crea la struttura base
        if not os.path.exists(self.filename):
            plants = [{
                "plant_id": self.plant_descriptor.plant_id,
                "sensors": [],
                "actuators": [],
                "alerts": []
            }]
        else:
            with open(self.filename, "r") as f:
                plants = json.load(f)

        for plant in plants:
            if plant["plant_id"] == self.plant_descriptor.plant_id:
                # Assicurati che la sezione alerts esista
                if "alerts" not in plant:
                    plant["alerts"] = []
                
                # Aggiungi i nuovi alert (evita duplicati)
                for alert_message in alerts:
                    # Controlla se questo alert esiste già negli ultimi 5 minuti
                    recent_alerts = [
                        alert for alert in plant["alerts"] 
                        if alert.get("message") == alert_message and 
                        (timestamp - int(alert.get("timestamp", 0))) < 300  # 5 minuti
                    ]
                    
                    if not recent_alerts:  # Solo se non esiste già
                        alert_entry = {
                            "message": alert_message,
                            "timestamp": str(timestamp),
                            "type": "warning",  # Default type, può essere migliorato
                            "plant_id": self.plant_descriptor.plant_id
                        }
                        plant["alerts"].append(alert_entry)
                        logging.info(f"Stored alert: {alert_message}")
                    else:
                        logging.debug(f"Skipped duplicate alert: {alert_message}")
                break

        with open(self.filename, "w") as f:
            json.dump(plants, f, indent=2)

