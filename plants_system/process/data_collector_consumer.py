import logging
import time
import paho.mqtt.client as mqtt
import json
import os
import asyncio
import threading
import concurrent.futures
from conf.mqtt_conf_params import MqttConfigurationParameters
from plants_system.smart_objects.models.plant_descriptor import PlantDescriptor
from plants_system.process.policy_manager import PolicyManager
from plants_system.process.data_collector_producer import DataCollectorProducer

class DataCollectorConsumer:
    """
    Consumer MQTT per la raccolta e elaborazione dei dati delle piante.
    
    Questa classe gestisce la ricezione di messaggi MQTT dai sensori delle piante,
    l'elaborazione dei dati, la valutazione delle policy e la persistenza dei dati
    nei file JSON. È responsabile dell'intero ciclo di vita dei dati IoT.
    """
    def __init__(self, plant_descriptor: PlantDescriptor, path:str):
        self.plant_descriptor = plant_descriptor
        self.filename=path+self.plant_descriptor.plant_id+".json"
        client_id = f"{self.plant_descriptor.plant_id}-data-collector-consumer"
        self.client = mqtt.Client(client_id)
        self.client.on_connect = self.on_connect
        self.client.on_message = self.on_message
        self.policy_manager = PolicyManager("plants_system/smart_objects/resources/policies_conf.json")
        self.running = False
        #TODO
        
        # Controllo frequenza aggiornamenti (minimo 1 secondo tra aggiornamenti)
        self.last_update_time = 0
        self.min_update_interval = 1.0  # secondi
        
        # Thread pool per operazioni async
        self.executor = concurrent.futures.ThreadPoolExecutor(max_workers=2)
        self.loop = None
        self.pending_tasks = set()  # Traccia le task in esecuzione
        self.last_cleanup = time.time()  # Timestamp dell'ultima pulizia
 
    """
    Callback per la connessione MQTT.
    
    Questo metodo viene chiamato quando il consumer si connette al broker MQTT.
    """
    def on_connect(self, client, userdata, flags, rc):
        logging.info("Connected with result code %s", str(rc))
        for device in self.plant_descriptor.devices:
            for sensor in device.sensors:
                    topic = MqttConfigurationParameters.build_telemetry_plant_topic(
                        self.plant_descriptor.plant_id, sensor.device, sensor.type
                    )
                    self.client.subscribe(topic)
                    print(f"Subscribed to topic: {topic}")
        

    """
    Callback per la ricezione di messaggi MQTT.
    
    Questo metodo viene chiamato quando il consumer riceve un messaggio MQTT.
    """
    def on_message(self, client, userdata, msg):
        """
        Callback ottimizzato per la ricezione di messaggi MQTT.
        
        Questo metodo è stato ottimizzato per essere il più veloce possibile:
        - Parsing minimo del messaggio
        - Esecuzione asincrona dell'elaborazione
        - Nessuna operazione I/O sincrona
        """
        # Controlla se il sistema è ancora attivo
        if not self.running:
            logging.debug("Skipping message - system is shutting down")
            return
            
        try:
            message_payload = msg.payload.decode("utf-8")
            logging.debug(f"Received message on topic {msg.topic}")
            
            # Parsing veloce solo dei campi essenziali
            data = json.loads(message_payload)
            message_data = {
                'topic': msg.topic,
                'payload': message_payload,
                'sensor_type': data.get("type"),
                'value': data.get("value"),
                'device_name': data.get("device"),
                'timestamp': data.get("timestamp", int(time.time()))
            }
            
            # Esegui l'elaborazione in modo asincrono
            if self.loop and not self.loop.is_closed():
                task = asyncio.run_coroutine_threadsafe(
                    self._process_message_async(message_data), 
                    self.loop
                )
                # Traccia la task per poterla cancellare in seguito
                self.pending_tasks.add(task)
                
                # Pulisci le task completate ogni 30 secondi
                current_time = time.time()
                if current_time - self.last_cleanup > 30:
                    self._cleanup_completed_tasks()
                    self.last_cleanup = current_time
            
        except Exception as e:
            logging.error(f"Error in on_message: {e}")
    
    def _cleanup_completed_tasks(self):
        """
        Pulisce le task completate dal set delle task pendenti.
        
        Questo metodo rimuove le task che sono state completate o cancellate
        per evitare memory leaks e mantenere il set delle task pulito.
        """
        completed_tasks = set()
        for task in self.pending_tasks:
            if task.done():
                completed_tasks.add(task)
        
        # Rimuovi le task completate
        self.pending_tasks -= completed_tasks
        
        if completed_tasks:
            logging.debug(f"Cleaned up {len(completed_tasks)} completed tasks")
    
    async def _process_message_async(self, message_data):
        """
        Processa un messaggio MQTT in modo asincrono.
        
        Questo metodo contiene tutta la logica di elaborazione che prima era nel callback on_message:
        - Aggiornamento PlantDescriptor
        - Scrittura su file JSON (async)
        - Valutazione policy (async)
        - Gestione alert e azioni (async)
        """
        # Controlla se il sistema è ancora attivo
        if not self.running:
            logging.debug("Skipping message processing - system is shutting down")
            return
            
        try:
            sensor_type = message_data['sensor_type']
            value = message_data['value']
            device_name = message_data['device_name']
            
            logging.info(f"Processing message: {sensor_type}={value} from {device_name}")

            # Aggiorna il sensore corrispondente nel plant_descriptor
            for device in self.plant_descriptor.devices:
                if device.device == device_name:
                    for sensor in device.sensors:
                        if sensor.type == sensor_type:
                            sensor.value = value
                            logging.debug(f"Updated sensor {sensor.type} of {device.device} to {sensor.value}")
                            break

            # Aggiorna la storia del sensore nel file json (async)
            await self._update_sensor_history_async(sensor_type, value, device_name)

            # Rivaluta le policy (async)
            logging.info(f"Evaluating policies for plant {self.plant_descriptor.plant_id}")
            await self._evaluate_policies_async()
            alerts = self.policy_manager.alerts.get(self.plant_descriptor.plant_id, [])
            actions = self.policy_manager.actions.get(self.plant_descriptor.plant_id, [])
            
            logging.info(f"Plant {self.plant_descriptor.plant_id} - Alerts: {len(alerts)}, Actions: {len(actions)}")
            for alert in alerts:
                print(f"ALERT: {alert}")
                logging.info(f"ALERT: {alert}")
            
            # Salva gli alert nei file JSON (async)
            if alerts:
                logging.info(f"Saving {len(alerts)} alerts to JSON file")
                await self._update_alerts_history_async(alerts)
            else:
                logging.debug(f"No alerts to save for plant {self.plant_descriptor.plant_id}")

            # Esegui solo le azioni relative al sensore appena aggiornato (async)
            await self._process_actions_async(actions, sensor_type)
                        
        except Exception as e:
            logging.error(f"Error processing message: {e}")
        finally:
            # Rimuovi la task completata dal set delle task pendenti
            # Nota: questo viene fatto automaticamente quando la task completa
            pass
    
    async def _update_sensor_history_async(self, sensor_type, value, device_name):
        """Aggiorna la storia del sensore in modo asincrono."""
        loop = asyncio.get_event_loop()
        await loop.run_in_executor(
            self.executor, 
            self.update_sensor_history, 
            sensor_type, value, device_name
        )
    
    async def _evaluate_policies_async(self):
        """Valuta le policy in modo asincrono."""
        loop = asyncio.get_event_loop()
        await loop.run_in_executor(
            self.executor,
            self.policy_manager.evaluate,
            self.plant_descriptor
        )
    
    async def _update_alerts_history_async(self, alerts):
        """Aggiorna la storia degli alert in modo asincrono."""
        loop = asyncio.get_event_loop()
        await loop.run_in_executor(
            self.executor,
            self.update_alerts_history,
            alerts
        )
    
    async def _process_actions_async(self, actions, sensor_type):
        """Processa le azioni in modo asincrono."""
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
                    # Controlla lo stato attuale dell'attuatore dal file JSON
                    current_actuator_state = await self._get_current_actuator_state_async(actuator_type)
                    
                    # Solo se lo stato deve cambiare
                    if current_actuator_state != desired_value:
                        print(f"ACTION: {action} (current: {current_actuator_state}, desired: {desired_value})")
                        await self._update_actuator_history_async(action)
                        await self._send_command_async(action)
                    else:
                        logging.info(f"No ACTION: {action} (actuator already in desired state: {current_actuator_state})")
                    break  # esegui solo una volta per questa azione
    
    async def _get_current_actuator_state_async(self, actuator_type):
        """Ottiene lo stato attuale di un attuatore in modo asincrono."""
        loop = asyncio.get_event_loop()
        return await loop.run_in_executor(
            self.executor,
            self._get_current_actuator_state,
            actuator_type
        )
    
    async def _update_actuator_history_async(self, action):
        """Aggiorna la storia dell'attuatore in modo asincrono."""
        loop = asyncio.get_event_loop()
        await loop.run_in_executor(
            self.executor,
            self.update_actuator_history,
            action
        )
    
    async def _send_command_async(self, action):
        """Invia un comando in modo asincrono."""
        loop = asyncio.get_event_loop()
        await loop.run_in_executor(
            self.executor,
            self._send_command_sync,
            action
        )
    
    def _send_command_sync(self, action):
        """Invia un comando in modo sincrono (per il thread pool)."""
        data_collector_producer = DataCollectorProducer(self.plant_descriptor, action)
        data_collector_producer.run()
    
    def run(self):
        """
        Avvia il consumer MQTT e mantiene la connessione attiva.
        
        Si connette al broker MQTT e inizia il loop di ricezione messaggi.
        Avvia anche l'event loop asyncio per gestire le operazioni asincrone.
        Il metodo rimane in esecuzione fino a quando non viene chiamato stop().
        """
        # Avvia l'event loop asyncio in un thread separato
        def run_async_loop():
            self.loop = asyncio.new_event_loop()
            asyncio.set_event_loop(self.loop)
            self.loop.run_forever()
        
        async_thread = threading.Thread(target=run_async_loop, daemon=True)
        async_thread.start()
        
        # Attendi che l'event loop sia pronto
        time.sleep(0.1)
        
        self.client.connect(MqttConfigurationParameters.BROKER_ADDRESS, MqttConfigurationParameters.BROKER_PORT)
        self.client.loop_start()
        self.running = True
        
        try:
            while self.running:
                time.sleep(1)
        finally:
            self.client.loop_stop()
            # Ferma l'event loop asyncio
            if self.loop and not self.loop.is_closed():
                self.loop.call_soon_threadsafe(self.loop.stop)
            async_thread.join(timeout=5.0)

    """
    Interrompe il consumer MQTT e termina la connessione.
    
    Questo metodo chiude il loop di ricezione messaggi e si disconnette dal broker MQTT.
    """
    def stop(self):
        """
        Interrompe il consumer MQTT e termina la connessione.
        
        Questo metodo chiude il loop di ricezione messaggi, si disconnette dal broker MQTT
        e ferma l'event loop asyncio.
        """
        self.running = False
        self.client.disconnect()
        
        # Ferma l'event loop asyncio
        if self.loop and not self.loop.is_closed():
            # Cancella tutte le task pendenti e aspetta che finiscano
            if self.pending_tasks:
                logging.info(f"Cancelling {len(self.pending_tasks)} pending tasks...")
                for task in self.pending_tasks.copy():
                    if not task.done():
                        task.cancel()
                        logging.debug(f"Cancelled pending task: {task}")
                
                # Aspetta che tutte le task vengano cancellate
                import asyncio
                try:
                    # Filtra solo le task valide (non cancellate e non completate)
                    valid_tasks = [task for task in self.pending_tasks if not task.done() and not task.cancelled()]
                    
                    if valid_tasks:
                        # Crea una task per aspettare tutte le cancellazioni
                        async def wait_for_cancellation():
                            await asyncio.gather(*valid_tasks, return_exceptions=True)
                        
                        # Esegui l'attesa in modo sincrono con timeout
                        future = asyncio.run_coroutine_threadsafe(wait_for_cancellation(), self.loop)
                        future.result(timeout=2.0)  # Timeout di 2 secondi
                    else:
                        logging.debug("No valid tasks to wait for")
                        
                except Exception as e:
                    logging.warning(f"Error waiting for task cancellation: {e}")
            
            # Pulisci il set delle task
            self.pending_tasks.clear()
            
            # Ferma l'event loop
            self.loop.call_soon_threadsafe(self.loop.stop)
        
        # Chiudi il thread pool con timeout
        try:
            self.executor.shutdown(wait=False)  # Non aspettare indefinitamente
        except Exception as e:
            logging.warning(f"Error shutting down executor: {e}")
            
        logging.info("DataCollectorConsumer stopped...")


    """
        Aggiorna la cronologia dei valori dei sensori nel file JSON.
        
        Salva i nuovi valori dei sensori nel file JSON, evitando duplicati
        consecutivi e mantenendo un timestamp per ogni misurazione.
        
    """
    def _safe_write_json(self, data):
        """
        Scrive i dati in modo sicuro nel file JSON con gestione degli errori.
        
        Args:
            data: Dati da scrivere nel file JSON
            
        Returns:
            bool: True se la scrittura è riuscita, False altrimenti
        """
        try:
            with open(self.filename, "w") as f:
                json.dump(data, f, indent=2)
            return True
        except Exception as e:
            logging.error(f"Error writing JSON file {self.filename}: {e}")
            return False
    
    def _safe_read_json(self):
        """
        Legge i dati dal file JSON in modo sicuro con gestione degli errori.
        
        Returns:
            list: Lista dei dati delle piante o lista vuota se errore
        """
        try:
            if not os.path.exists(self.filename):
                return []
            
            with open(self.filename, "r") as f:
                data = json.load(f)
                return data if isinstance(data, list) else []
                
        except json.JSONDecodeError as e:
            logging.error(f"JSON decode error in {self.filename}: {e}")
            return []
        except Exception as e:
            logging.error(f"Error reading JSON file {self.filename}: {e}")
            return []
    def update_sensor_history(self, sensor_type, value, device_name):
        """
        Aggiorna la cronologia dei sensori nel file JSON.
        
        Salva i nuovi valori dei sensori nel file JSON, evitando duplicati
        consecutivi e mantenendo un timestamp per ogni misurazione.
        """
        # Controllo frequenza aggiornamenti
        current_time = time.time()
        if current_time - self.last_update_time < self.min_update_interval:
            logging.debug(f"Skipping sensor update for {sensor_type} - too frequent")
            return
        
        self.last_update_time = current_time
        timestamp = int(time.time())
        
        # Leggi i dati esistenti in modo sicuro
        plants = self._safe_read_json()
        
        # Se il file non esiste o è vuoto, crea la struttura base
        if not plants:
            plants = [{
                "plant_id": self.plant_descriptor.plant_id,
                "sensors": [],
                "actuators": [],
                "alerts": []
            }]

        # Trova o crea la pianta
        plant_found = False
        for plant in plants:
            if plant["plant_id"] == self.plant_descriptor.plant_id:
                plant_found = True
                break
        
        if not plant_found:
            plants.append({
                "plant_id": self.plant_descriptor.plant_id,
                "sensors": [],
                "actuators": [],
                "alerts": []
            })
            plant = plants[-1]
        else:
            plant = next(p for p in plants if p["plant_id"] == self.plant_descriptor.plant_id)

        # Assicurati che la sezione sensors esista
        if "sensors" not in plant:
            plant["sensors"] = []

        # Trova o crea il sensore
        sensor_found = False
        for s in plant["sensors"]:
            if s.get("sensor") == sensor_type and s.get("device") == device_name:
                sensor_found = True
                if "values" not in s:
                    s["values"] = []
                # Solo memorizzare se il valore è cambiato
                if not s["values"] or s["values"][-1]["value"] != value:
                    s["values"].append({"value": value, "timestamp": str(timestamp)})
                    logging.info(f"Stored new sensor value: {sensor_type} = {value}")
                else:
                    logging.debug(f"Skipped duplicate sensor value: {sensor_type} = {value}")
                break
        
        if not sensor_found:
            plant["sensors"].append({
                "sensor": sensor_type,
                "device": device_name,
                "values": [{"value": value, "timestamp": str(timestamp)}]
            })
            logging.info(f"Created new sensor entry: {sensor_type} = {value}")

        # Scrivi i dati in modo sicuro
        if not self._safe_write_json(plants):
            logging.error(f"Failed to write sensor data for {sensor_type}")

    
    def update_actuator_history(self, action):
        """
        Aggiorna la cronologia degli attuatori nel file JSON.
        
        Salva i nuovi valori degli attuatori nel file JSON, evitando duplicati
        consecutivi e mantenendo un timestamp per ogni azione.
        """
        # Controllo frequenza aggiornamenti
        current_time = time.time()
        if current_time - self.last_update_time < self.min_update_interval:
            logging.debug(f"Skipping actuator update for {action} - too frequent")
            return
        
        self.last_update_time = current_time
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

        # Leggi i dati esistenti in modo sicuro
        plants = self._safe_read_json()
        
        # Se il file non esiste o è vuoto, crea la struttura base
        if not plants:
            plants = [{
                "plant_id": self.plant_descriptor.plant_id,
                "sensors": [],
                "actuators": [],
                "alerts": []
            }]

        # Trova o crea la pianta
        plant_found = False
        for plant in plants:
            if plant["plant_id"] == self.plant_descriptor.plant_id:
                plant_found = True
                break
        
        if not plant_found:
            plants.append({
                "plant_id": self.plant_descriptor.plant_id,
                "sensors": [],
                "actuators": [],
                "alerts": []
            })
            plant = plants[-1]
        else:
            plant = next(p for p in plants if p["plant_id"] == self.plant_descriptor.plant_id)

        # Assicurati che la sezione actuators esista
        if "actuators" not in plant:
            plant["actuators"] = []

        # Trova o crea l'attuatore
        actuator_found = False
        for a in plant["actuators"]:
            if a.get("actuator") == actuator_type and a.get("device") == device_name:
                actuator_found = True
                if "values" not in a:
                    a["values"] = []
                # Solo memorizzare se il valore è cambiato
                if not a["values"] or a["values"][-1]["value"] != value:
                    a["values"].append({"value": value, "timestamp": str(timestamp)})
                    logging.info(f"Stored new actuator value: {actuator_type} = {value}")
                else:
                    logging.debug(f"Skipped duplicate actuator value: {actuator_type} = {value}")
                break
        
        if not actuator_found:
            plant["actuators"].append({
                "actuator": actuator_type,
                "device": device_name,
                "values": [{"value": value, "timestamp": str(timestamp)}]
            })
            logging.info(f"Created new actuator entry: {actuator_type} = {value}")

        # Scrivi i dati in modo sicuro
        if not self._safe_write_json(plants):
            logging.error(f"Failed to write actuator data for {actuator_type}")

    def update_alerts_history(self, alerts):
        """
        Salva le cronologie degli alert nel file JSON.
        
        Salva le nuove alert nel file JSON, evitando duplicati consecutivi
        e mantenendo un timestamp per ogni alert.
        """
        # Controllo frequenza aggiornamenti
        current_time = time.time()
        if current_time - self.last_update_time < self.min_update_interval:
            logging.debug(f"Skipping alerts update - too frequent")
            return
        
        self.last_update_time = current_time
        timestamp = int(time.time())
        
        # Leggi i dati esistenti in modo sicuro
        plants = self._safe_read_json()
        
        # Se il file non esiste o è vuoto, crea la struttura base
        if not plants:
            plants = [{
                "plant_id": self.plant_descriptor.plant_id,
                "sensors": [],
                "actuators": [],
                "alerts": []
            }]

        # Trova o crea la pianta
        plant_found = False
        for plant in plants:
            if plant["plant_id"] == self.plant_descriptor.plant_id:
                plant_found = True
                break
        
        if not plant_found:
            plants.append({
                "plant_id": self.plant_descriptor.plant_id,
                "sensors": [],
                "actuators": [],
                "alerts": []
            })
            plant = plants[-1]
        else:
            plant = next(p for p in plants if p["plant_id"] == self.plant_descriptor.plant_id)

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

        # Scrivi i dati in modo sicuro
        if not self._safe_write_json(plants):
            logging.error(f"Failed to write alerts data")

    def _get_current_actuator_state(self, actuator_type):
        """
        Ottiene lo stato attuale di un attuatore dal file JSON.
        
        Args:
            actuator_type (str): Tipo di attuatore (es. 'irrigation')
            
        Returns:
            bool: Stato attuale dell'attuatore (True/False) o False se non trovato
        """
        try:
            if not os.path.exists(self.filename):
                return False
                
            with open(self.filename, "r") as f:
                plants = json.load(f)
                
            for plant in plants:
                if plant["plant_id"] == self.plant_descriptor.plant_id:
                    actuators = plant.get("actuators", [])
                    for actuator in actuators:
                        if actuator.get("actuator") == actuator_type:
                            values = actuator.get("values", [])
                            if values:
                                return values[-1].get("value", False)
                    break
        except Exception as e:
            logging.error(f"Error reading actuator state: {e}")
            
        return False

