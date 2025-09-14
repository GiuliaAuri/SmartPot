import json
import os
import logging
import time
from typing import List, Dict, Any, Optional


class JsonManager:
    """
    Gestisce tutte le operazioni di lettura e scrittura sui file JSON.
    
    Questa classe centralizza la gestione dei file JSON per evitare duplicazione
    di codice e migliorare la manutenibilità.
    """
    
    def __init__(self, filename: str):
        self.filename = filename
    
    def read_data(self) -> List[Dict[str, Any]]:
        """
        Legge i dati dal file JSON in modo sicuro.
        
        Returns:
            List[Dict]: Lista dei dati delle piante o lista vuota se errore
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
    
    def write_data(self, data: List[Dict[str, Any]]) -> bool:
        """
        Scrive i dati nel file JSON in modo sicuro.
        
        Args:
            data: Lista dei dati da scrivere
            
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
    
    def find_or_create_plant(self, plants: List[Dict[str, Any]], plant_id: str) -> Dict[str, Any]:
        """
        Trova una pianta esistente o ne crea una nuova.
        
        Args:
            plants: Lista delle piante
            plant_id: ID della pianta da cercare/creare
            
        Returns:
            Dict: Dati della pianta trovata o creata
        """
        # Trova la pianta esistente
        for plant in plants:
            if plant["plant_id"] == plant_id:
                return plant
        
        # Crea una nuova pianta se non esiste
        new_plant = {
            "plant_id": plant_id,
            "sensors": [],
            "actuators": [],
            "alerts": []
        }
        plants.append(new_plant)
        return new_plant
    
    def update_sensor_value(self, plant_id: str, sensor_type: str, value: Any, device_name: str) -> bool:
        """
        Aggiorna il valore di un sensore nel file JSON.
        
        Args:
            plant_id: ID della pianta
            sensor_type: Tipo di sensore
            value: Nuovo valore
            device_name: Nome del dispositivo
            
        Returns:
            bool: True se l'aggiornamento è riuscito
        """
        plants = self.read_data()
        if not plants:
            plants = []
        
        plant = self.find_or_create_plant(plants, plant_id)
        
        # Assicurati che la sezione sensors esista
        if "sensors" not in plant:
            plant["sensors"] = []
        
        # Trova o crea il sensore
        sensor_found = False
        for sensor in plant["sensors"]:
            if sensor.get("sensor") == sensor_type and sensor.get("device") == device_name:
                sensor_found = True
                if "values" not in sensor:
                    sensor["values"] = []
                
                # Solo memorizzare se il valore è cambiato
                if not sensor["values"] or sensor["values"][-1]["value"] != value:
                    sensor["values"].append({
                        "value": value, 
                        "timestamp": str(int(time.time()))
                    })
                    logging.info(f"Stored new sensor value: {sensor_type} = {value}")
                else:
                    logging.debug(f"Skipped duplicate sensor value: {sensor_type} = {value}")
                break
        
        if not sensor_found:
            plant["sensors"].append({
                "sensor": sensor_type,
                "device": device_name,
                "values": [{"value": value, "timestamp": str(int(time.time()))}]
            })
            logging.info(f"Created new sensor entry: {sensor_type} = {value}")
        
        return self.write_data(plants)
    
    def update_actuator_value(self, plant_id: str, actuator_type: str, value: bool, device_name: str) -> bool:
        """
        Aggiorna il valore di un attuatore nel file JSON.
        
        Args:
            plant_id: ID della pianta
            actuator_type: Tipo di attuatore
            value: Nuovo valore (True/False)
            device_name: Nome del dispositivo
            
        Returns:
            bool: True se l'aggiornamento è riuscito
        """
        plants = self.read_data()
        if not plants:
            plants = []
        
        plant = self.find_or_create_plant(plants, plant_id)
        
        # Assicurati che la sezione actuators esista
        if "actuators" not in plant:
            plant["actuators"] = []
        
        # Trova o crea l'attuatore
        actuator_found = False
        for actuator in plant["actuators"]:
            if actuator.get("type") == actuator_type and actuator.get("device") == device_name:
                actuator_found = True
                if "values" not in actuator:
                    actuator["values"] = []
                
                # Solo memorizzare se il valore è cambiato
                if not actuator["values"] or actuator["values"][-1]["value"] != value:
                    actuator["values"].append({
                        "value": value, 
                        "timestamp": str(int(time.time()))
                    })
                    logging.info(f"Stored new actuator value: {actuator_type} = {value}")
                else:
                    logging.debug(f"Skipped duplicate actuator value: {actuator_type} = {value}")
                break
        
        if not actuator_found:
            plant["actuators"].append({
                "type": actuator_type,
                "device": device_name,
                "values": [{"value": value, "timestamp": str(int(time.time()))}]
            })
            logging.info(f"Created new actuator entry: {actuator_type} = {value}")
        
        return self.write_data(plants)
    
    def add_alerts(self, plant_id: str, alerts: List[str]) -> bool:
        """
        Aggiunge nuovi alert al file JSON.
        
        Args:
            plant_id: ID della pianta
            alerts: Lista dei messaggi di alert
            
        Returns:
            bool: True se l'aggiornamento è riuscito
        """
        plants = self.read_data()
        if not plants:
            plants = []
        
        plant = self.find_or_create_plant(plants, plant_id)
        
        # Assicurati che la sezione alerts esista
        if "alerts" not in plant:
            plant["alerts"] = []
        
        timestamp = int(time.time())
        
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
                    "type": "warning",
                    "plant_id": plant_id
                }
                plant["alerts"].append(alert_entry)
                logging.info(f"Stored alert: {alert_message}")
            else:
                logging.debug(f"Skipped duplicate alert: {alert_message}")
        
        return self.write_data(plants)
    
    def get_actuator_state(self, plant_id: str, actuator_type: str) -> bool:
        """
        Ottiene lo stato attuale di un attuatore dal file JSON.
        
        Args:
            plant_id: ID della pianta
            actuator_type: Tipo di attuatore
            
        Returns:
            bool: Stato attuale dell'attuatore o False se non trovato
        """
        plants = self.read_data()
        
        for plant in plants:
            if plant["plant_id"] == plant_id:
                actuators = plant.get("actuators", [])
                for actuator in actuators:
                    if actuator.get("type") == actuator_type:
                        values = actuator.get("values", [])
                        if values:
                            return values[-1].get("value", False)
                break
        
        return False
    
    def initialize_actuators(self, plant_id: str, plant_descriptor) -> bool:
        """
        Inizializza gli attuatori nel file JSON se non esistono.
        
        Args:
            plant_id: ID della pianta
            plant_descriptor: Descrittore della pianta
            
        Returns:
            bool: True se l'inizializzazione è riuscita
        """
        plants = self.read_data()
        if not plants:
            plants = []
        
        plant = self.find_or_create_plant(plants, plant_id)
        
        # Assicurati che la sezione actuators esista
        if "actuators" not in plant:
            plant["actuators"] = []
        
        # Inizializza tutti gli attuatori definiti nella configurazione
        for device in plant_descriptor.devices:
            for actuator in getattr(device, "actuators", []):
                actuator_type = getattr(actuator, "type", None)
                if actuator_type:
                    # Controlla se l'attuatore esiste già
                    actuator_exists = False
                    for existing_actuator in plant["actuators"]:
                        if existing_actuator.get("type") == actuator_type:
                            actuator_exists = True
                            break
                    
                    # Se non esiste, crealo con stato iniziale False
                    if not actuator_exists:
                        plant["actuators"].append({
                            "type": actuator_type,
                            "device": device.device,
                            "values": [{"value": False, "timestamp": str(int(time.time()))}]
                        })
                        logging.info(f"Initialized actuator {actuator_type} with state False")
        
        return self.write_data(plants)
    
    def get_recent_actuator_changes(self, plant_id: str, max_age_seconds: int = 5) -> List[Dict[str, Any]]:
        """
        Ottiene gli attuatori che hanno cambiato stato di recente.
        
        Args:
            plant_id: ID della pianta
            max_age_seconds: Massima età dei cambiamenti in secondi
            
        Returns:
            List[Dict]: Lista degli attuatori con cambiamenti recenti
        """
        plants = self.read_data()
        recent_changes = []
        current_time = int(time.time())
        
        for plant in plants:
            if plant["plant_id"] == plant_id:
                actuators = plant.get("actuators", [])
                for actuator in actuators:
                    if "values" not in actuator or not actuator["values"]:
                        continue
                    
                    # Prendi l'ultimo valore
                    last_value = actuator["values"][-1]
                    timestamp = int(last_value["timestamp"])
                    
                    # Controlla se questo è un cambiamento recente
                    if current_time - timestamp <= max_age_seconds:
                        recent_changes.append({
                            "type": actuator.get("type"),
                            "device": actuator.get("device"),
                            "value": last_value["value"],
                            "timestamp": timestamp
                        })
                break
        
        return recent_changes
