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
from plants_system.process.json_manager import JsonManager


class DataCollectorConsumer:
    """
    Consumer MQTT semplificato per la raccolta e elaborazione dei dati delle piante.
    
    Questa versione è molto più semplice e leggibile:
    - Usa JsonManager per tutte le operazioni sui file JSON
    - Mantiene la logica MQTT interna
    - Mantiene la logica delle policy nel PolicyManager
    - Struttura più chiara e facile da leggere
    """
    
    def __init__(self, plant_descriptor: PlantDescriptor, path: str):
        # FORZA TUTTI I SENSORI E ATTUATORI IN MODALITÀ SIMULATA
        # Il data_collector NON deve mai comunicare con Arduino
        self._force_simulation_mode(plant_descriptor)
        
        self.plant_descriptor = plant_descriptor
        self.running = False
        
        # Inizializza i componenti
        self.json_manager = JsonManager(path + plant_descriptor.plant_id + ".json")
        self.policy_manager = PolicyManager("plants_system/smart_objects/resources/policies_conf.json")
        
        # Configurazione MQTT
        client_id = f"{plant_descriptor.plant_id}-data-collector-consumer"
        try:
            self.client = mqtt.Client(mqtt.CallbackAPIVersion.VERSION1, client_id)
        except AttributeError:
            self.client = mqtt.Client(client_id)
        
        self.client.on_connect = self.on_connect
        self.client.on_message = self.on_message
        
        # Configurazione polling
        self.polling_interval = 2.0  # secondi
        self.last_polling_time = 0
        
        # Thread pool per operazioni async
        self.executor = concurrent.futures.ThreadPoolExecutor(max_workers=2)
        self.loop = None
        self.pending_tasks = set()
        
        # Controllo frequenza aggiornamenti
        self.last_update_time = 0
        self.min_update_interval = 1.0
    
    def _force_simulation_mode(self, plant_descriptor: PlantDescriptor):
        """
        Forza tutti i sensori e attuatori in modalità simulata.
        Il data_collector NON deve mai comunicare con Arduino.
        """
        logging.info(f"Forzando modalità simulata per tutti i dispositivi di {plant_descriptor.plant_id}")
        
        for device in plant_descriptor.devices:
            # Forza tutti i sensori in modalità simulata
            for sensor in device.sensors:
                if sensor.is_real:
                    logging.info(f"Sensore {sensor.type} forzato in modalità simulata")
                    sensor.is_real = False
            
            # Forza tutti gli attuatori in modalità simulata
            for actuator in device.actuators:
                if actuator.is_real:
                    logging.info(f"Attuatore {actuator.type} forzato in modalità simulata")
                    actuator.is_real = False
    
    def on_connect(self, client, userdata, flags, rc):
        """Callback per la connessione MQTT."""
        logging.info("Connected with result code %s", str(rc))
        if rc == 0:
            # Sottoscriviti ai topic dei sensori
            for device in self.plant_descriptor.devices:
                for sensor in device.sensors:
                    topic = MqttConfigurationParameters.build_telemetry_plant_topic(
                        self.plant_descriptor.plant_id, sensor.device, sensor.type
                    )
                    self.client.subscribe(topic)
                    logging.info(f"Subscribed to topic: {topic}")
    
    def on_message(self, client, userdata, msg):
        """
        Callback per la ricezione di messaggi MQTT.
        
        Questo metodo è molto più semplice: riceve il messaggio e delega
        l'elaborazione a un metodo asincrono.
        """
        if not self.running:
            return
        
        try:
            message_payload = msg.payload.decode("utf-8")
            logging.debug(f"Received message on topic {msg.topic}")
            
            # Parsing veloce del messaggio
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
                if len(self.pending_tasks) >= 50:  # Limite task pendenti
                    logging.warning("Too many pending tasks, skipping message")
                    return
                
                task = asyncio.run_coroutine_threadsafe(
                    self._process_message_async(message_data), 
                    self.loop
                )
                self.pending_tasks.add(task)
            
        except Exception as e:
            logging.error(f"Error in on_message: {e}")
    
    async def _process_message_async(self, message_data):
        """
        Processa un messaggio MQTT in modo asincrono.
        
        Questo metodo orchestrra tutte le operazioni necessarie:
        1. Aggiorna il sensore nel PlantDescriptor
        2. Salva il valore nel JSON
        3. Valuta le policy
        4. Salva gli alert
        5. Esegue le azioni
        """
        if not self.running:
            return
        
        try:
            sensor_type = message_data['sensor_type']
            value = message_data['value']
            device_name = message_data['device_name']
            
            logging.info(f"Processing message: {sensor_type}={value} from {device_name}")
            
            # 1. Aggiorna il sensore nel PlantDescriptor
            self._update_sensor_in_descriptor(sensor_type, value, device_name)
            
            # 2. Salva il valore nel JSON (async)
            await self._save_sensor_value_async(sensor_type, value, device_name)
            
            # 3. Valuta le policy (async)
            alerts, actions = await self._evaluate_policies_async()
            
            # 4. Salva gli alert (async)
            if alerts:
                await self._save_alerts_async(alerts)
            
            # 5. Esegue le azioni (async)
            await self._execute_actions_async(actions, sensor_type)
            
        except Exception as e:
            logging.error(f"Error processing message: {e}")
    
    def _update_sensor_in_descriptor(self, sensor_type: str, value: float, device_name: str):
        """Aggiorna il valore del sensore nel PlantDescriptor."""
        for device in self.plant_descriptor.devices:
            if device.device == device_name:
                for sensor in device.sensors:
                    if sensor.type == sensor_type:
                        sensor.value = value
                        logging.debug(f"Updated sensor {sensor.type} of {device.device} to {sensor.value}")
                        break
    
    async def _save_sensor_value_async(self, sensor_type: str, value: float, device_name: str):
        """Salva il valore del sensore nel JSON in modo asincrono."""
        loop = asyncio.get_event_loop()
        await loop.run_in_executor(
            self.executor,
            self._save_sensor_value_sync,
            sensor_type, value, device_name
        )
    
    def _save_sensor_value_sync(self, sensor_type: str, value: float, device_name: str):
        """Salva il valore del sensore nel JSON (versione sincrona per il thread pool)."""
        # Controllo frequenza aggiornamenti
        current_time = time.time()
        if current_time - self.last_update_time < self.min_update_interval:
            logging.debug(f"Skipping sensor update for {sensor_type} - too frequent")
            return
        
        self.last_update_time = current_time
        self.json_manager.update_sensor_value(
            self.plant_descriptor.plant_id, 
            sensor_type, 
            value, 
            device_name
        )
    
    async def _evaluate_policies_async(self):
        """Valuta le policy in modo asincrono."""
        loop = asyncio.get_event_loop()
        return await loop.run_in_executor(
            self.executor,
            self.policy_manager.evaluate,
            self.plant_descriptor
        )
    
    async def _save_alerts_async(self, alerts: list):
        """Salva gli alert nel JSON in modo asincrono."""
        loop = asyncio.get_event_loop()
        await loop.run_in_executor(
            self.executor,
            self.json_manager.add_alerts,
            self.plant_descriptor.plant_id,
            alerts
        )
    
    async def _execute_actions_async(self, actions: list, sensor_type: str):
        """Esegue le azioni in modo asincrono."""
        for action in actions:
            action_parts = action.split()
            if len(action_parts) < 2:
                continue
            
            actuator_type = action_parts[1]
            desired_value = True if action_parts[0].lower() == "activate" else False
            
            # Controlla lo stato attuale dell'attuatore
            current_state = await self._get_actuator_state_async(actuator_type)
            
            # Solo se lo stato deve cambiare
            if current_state != desired_value:
                await self._update_actuator_state_async(actuator_type, desired_value)
                await self._send_command_async(action)
            else:
                logging.info(f"No ACTION: {actuator_type} already in desired state: {current_state}")
    
    async def _get_actuator_state_async(self, actuator_type: str) -> bool:
        """Ottiene lo stato attuale di un attuatore in modo asincrono."""
        loop = asyncio.get_event_loop()
        return await loop.run_in_executor(
            self.executor,
            self.json_manager.get_actuator_state,
            self.plant_descriptor.plant_id,
            actuator_type
        )
    
    async def _update_actuator_state_async(self, actuator_type: str, value: bool):
        """Aggiorna lo stato di un attuatore nel JSON in modo asincrono."""
        loop = asyncio.get_event_loop()
        await loop.run_in_executor(
            self.executor,
            self._update_actuator_state_sync,
            actuator_type,
            value
        )
    
    def _update_actuator_state_sync(self, actuator_type: str, value: bool):
        """Aggiorna lo stato di un attuatore nel JSON (versione sincrona)."""
        # Trova il device che contiene l'attuatore
        device_name = None
        for device in self.plant_descriptor.devices:
            for actuator in getattr(device, "actuators", []):
                if getattr(actuator, "type", None) == actuator_type:
                    device_name = device.device
                    break
            if device_name:
                break
        
        if device_name is None:
            device_name = actuator_type  # fallback
        
        self.json_manager.update_actuator_value(
            self.plant_descriptor.plant_id,
            actuator_type,
            value,
            device_name
        )
    
    async def _send_command_async(self, action: str):
        """Invia un comando MQTT in modo asincrono."""
        loop = asyncio.get_event_loop()
        await loop.run_in_executor(
            self.executor,
            self._send_command_sync,
            action
        )
    
    def _send_command_sync(self, action: str):
        """Invia un comando MQTT (versione sincrona)."""
        data_collector_producer = DataCollectorProducer(self.plant_descriptor, action)
        data_collector_producer.run()
    
    def _check_actuator_changes(self):
        """
        Controlla se ci sono stati cambiamenti negli attuatori nei file JSON.
        
        Questo metodo implementa il polling per rilevare cambiamenti manuali
        dall'interfaccia web.
        """
        try:
            recent_changes = self.json_manager.get_recent_actuator_changes(
                self.plant_descriptor.plant_id, 
                max_age_seconds=5
            )
            
            for change in recent_changes:
                self._send_actuator_command(change)
                
        except Exception as e:
            logging.error(f"Error checking actuator changes: {e}")
    
    def _send_actuator_command(self, actuator_data: dict):
        """
        Invia un comando MQTT per un attuatore specificato.
        
        Args:
            actuator_data: Dati dell'attuatore con cambiamento recente
        """
        try:
            actuator_type = actuator_data.get("type")
            device_name = actuator_data.get("device")
            state = actuator_data.get("value")
            
            if not actuator_type or not device_name:
                logging.warning(f"Incomplete actuator data: {actuator_data}")
                return
            
            # Determina il comando basato sullo stato
            command = "on" if state else "off"
            
            # Costruisci il topic MQTT
            topic = MqttConfigurationParameters.build_command_plant_topic(
                self.plant_descriptor.plant_id, 
                device_name
            )
            
            # Invia il comando MQTT
            self.client.publish(topic, command)
            logging.info(f"Sent actuator command: {command} to topic: {topic}")
            
        except Exception as e:
            logging.error(f"Error sending actuator command: {e}")
    
    def run(self):
        """
        Avvia il consumer MQTT e mantiene la connessione attiva.
        
        Questo metodo è molto più semplice e leggibile rispetto alla versione precedente.
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
        
        # Connetti al broker MQTT
        self.client.connect(MqttConfigurationParameters.BROKER_ADDRESS, MqttConfigurationParameters.BROKER_PORT)
        self.client.loop_start()
        self.running = True
        
        # Inizializza lo stato degli attuatori
        self.json_manager.initialize_actuators(
            self.plant_descriptor.plant_id, 
            self.plant_descriptor
        )
        
        # Loop principale con polling
        try:
            while self.running:
                current_time = time.time()
                
                # Polling per rilevare cambiamenti negli attuatori
                if current_time - self.last_polling_time >= self.polling_interval:
                    self._check_actuator_changes()
                    self.last_polling_time = current_time
                
                time.sleep(1)
                
        finally:
            self.stop()
    
    def stop(self):
        """
        Interrompe il consumer MQTT e termina la connessione.
        
        Questo metodo è molto più semplice e gestisce solo la pulizia essenziale.
        """
        logging.info("Stopping DataCollectorConsumer...")
        self.running = False
        
        # Disconnetti MQTT
        try:
            self.client.disconnect()
        except Exception as e:
            logging.warning(f"Error disconnecting MQTT client: {e}")
        
        # Gestisci le task asincrone pendenti
        if self.loop and not self.loop.is_closed():
            try:
                # Cancella tutte le task pendenti
                for task in self.pending_tasks.copy():
                    if not task.done():
                        task.cancel()
                
                # Ferma l'event loop
                self.loop.call_soon_threadsafe(self.loop.stop)
                
            except Exception as e:
                logging.warning(f"Error stopping event loop: {e}")
                self.pending_tasks.clear()
        
        # Chiudi il thread pool
        try:
            self.executor.shutdown(wait=False)
        except Exception as e:
            logging.warning(f"Error shutting down executor: {e}")
        
        logging.info("DataCollectorConsumer stopped successfully")
