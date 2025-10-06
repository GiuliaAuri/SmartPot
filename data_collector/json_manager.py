import json
import os
import time
from datetime import datetime
from typing import Dict, Any, List, Optional
import logging

class JsonManager:
    """
    Gestore per il salvataggio dei dati delle piante in file JSON.
    
    Ogni pianta ha un file JSON separato nella cartella cloud_simulator/plants_log/
    
    """
    
    def __init__(self, base_path: str = "cloud_simulator/plants_log"):
        """
        Inizializza il JsonManager.
        
        Args:
            base_path: Percorso base per i file JSON delle piante
        """
        self.base_path = base_path
        self._ensure_directory_exists()
        
    def _ensure_directory_exists(self):
        """Assicura che la directory esista."""
        if not os.path.exists(self.base_path):
            os.makedirs(self.base_path)
            logging.info(f"Creata directory: {self.base_path}")
    
    def _get_plant_file_path(self, plant_id: str) -> str:
        """Restituisce il percorso del file JSON per una pianta."""
        return os.path.join(self.base_path, f"{plant_id}.json")
    
    def _load_plant_data(self, plant_id: str) -> Dict[str, Any]:
        """
        Carica i dati di una pianta dal file JSON.
        
        Args:
            plant_id: ID della pianta
            
        Returns:
            Dizionario con i dati della pianta
        """
        file_path = self._get_plant_file_path(plant_id)
        
        if os.path.exists(file_path):
            try:
                with open(file_path, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                    
                
                if isinstance(data, dict):
                    return data
                else:
                    logging.warning(f"Formato file non supportato in {file_path}: {type(data)}")
                    return self._create_empty_plant_data(plant_id)
                    
            except (json.JSONDecodeError, IOError) as e:
                logging.warning(f"Errore caricamento file {file_path}: {e}")
                return self._create_empty_plant_data(plant_id)
        else:
            return self._create_empty_plant_data(plant_id)
    
    def _create_empty_plant_data(self, plant_id: str, species: str = "unknown") -> Dict[str, Any]:
        """
        Crea una struttura dati vuota per una pianta.
        
        Args:
            plant_id: ID della pianta
            species: Specie della pianta
            
        Returns:
            Struttura dati vuota
        """
        now = datetime.now()
        return {
            "plant_id": plant_id,
            "species": species,
            "created_at": now.isoformat() + "Z",
            "last_updated": now.isoformat() + "Z",
            "sensors": {},
            "actuators": {}
        }
    
    def _save_plant_data(self, plant_id: str, data: Dict[str, Any]):
        """
        Salva i dati di una pianta nel file JSON.
        
        Args:
            plant_id: ID della pianta
            data: Dati da salvare
        """
        file_path = self._get_plant_file_path(plant_id)
        
        try:
            # Aggiorna timestamp
            data["last_updated"] = datetime.now().isoformat() + "Z"
            
            with open(file_path, 'w', encoding='utf-8') as f:
                json.dump(data, f, indent=2, ensure_ascii=False)
                
            logging.debug(f"Dati salvati per {plant_id} in {file_path}")
            
        except IOError as e:
            logging.error(f"Errore salvataggio file {file_path}: {e}")
            raise
    
    def save_sensor_data(self, plant_id: str, sensor_type: str, value: float, 
                        species: str = "unknown", max_entries: int = 1000):
        """
        Salva i dati di un sensore per una pianta.
        
        Args:
            plant_id: ID della pianta
            sensor_type: Tipo di sensore (es. "humidity", "temperature")
            value: Valore del sensore
            species: Specie della pianta (per creazione file se non esiste)
            max_entries: Numero massimo di entry da mantenere per sensore
        """
        try:
            data = self._load_plant_data(plant_id)
            
            if data["species"] == "unknown" and species != "unknown":
                data["species"] = species
            
            if sensor_type not in data["sensors"]:
                data["sensors"][sensor_type] = []
            
            timestamp = int(time.time())
            entry = {
                "value": value,
                "timestamp": timestamp
            }
            
            data["sensors"][sensor_type].append(entry)
            
            if len(data["sensors"][sensor_type]) > max_entries:
                data["sensors"][sensor_type] = data["sensors"][sensor_type][-max_entries:]
            
            self._save_plant_data(plant_id, data)
            
            logging.info(f"Sensore {sensor_type} salvato per {plant_id}: {value}")
            
        except Exception as e:
            logging.error(f"Errore salvataggio sensore {sensor_type} per {plant_id}: {e}")
            raise
    
    def save_actuator_data(self, plant_id: str, actuator_type: str, action: str,
                          species: str = "unknown", max_entries: int = 1000):
        """
        Salva i dati di un attuatore per una pianta.
        
        Args:
            plant_id: ID della pianta
            actuator_type: Tipo di attuatore (es. "irrigation")
            action: Azione eseguita (es. "start", "stop")
            species: Specie della pianta (per creazione file se non esiste)
            max_entries: Numero massimo di entry da mantenere per attuatore
        """
        try:
            
            data = self._load_plant_data(plant_id)
            
            if data["species"] == "unknown" and species != "unknown":
                data["species"] = species
            
            if actuator_type not in data["actuators"]:
                data["actuators"][actuator_type] = []
            
            timestamp = int(time.time())
            entry = {
                "action": action,
                "timestamp": timestamp
            }
            
            data["actuators"][actuator_type].append(entry)
            
                
            if len(data["actuators"][actuator_type]) > max_entries:
                data["actuators"][actuator_type] = data["actuators"][actuator_type][-max_entries:]
            
            
            self._save_plant_data(plant_id, data)
            
            logging.info(f"Attuatore {actuator_type} salvato per {plant_id}: {action}")
            
        except Exception as e:
            logging.error(f"Errore salvataggio attuatore {actuator_type} per {plant_id}: {e}")
            raise
    
    def get_plant_data(self, plant_id: str) -> Optional[Dict[str, Any]]:
        """
        Recupera i dati di una pianta.
        
        Args:
            plant_id: ID della pianta
            
        Returns:
            Dati della pianta o None se non trovata
        """
        try:
            return self._load_plant_data(plant_id)
        except Exception as e:
            logging.error(f"Errore recupero dati per {plant_id}: {e}")
            return None
    
    def list_plants(self) -> List[str]:
        """
        Lista tutte le piante con file JSON.
        
        Returns:
            Lista degli ID delle piante
        """
        try:
            plants = []
            for filename in os.listdir(self.base_path):
                if filename.endswith('.json'):
                    plant_id = filename[:-5] 
                    plants.append(plant_id)
            return plants
        except Exception as e:
            logging.error(f"Errore lista piante: {e}")
            return []
    
    def get_latest_sensor_value(self, plant_id: str, sensor_type: str) -> Optional[float]:
        """
        Recupera l'ultimo valore di un sensore per una pianta.
        
        Args:
            plant_id: ID della pianta
            sensor_type: Tipo di sensore
            
        Returns:
            Ultimo valore del sensore o None se non trovato
        """
        try:
            data = self._load_plant_data(plant_id)
            if sensor_type in data["sensors"] and data["sensors"][sensor_type]:
                return data["sensors"][sensor_type][-1]["value"]
            return None
        except Exception as e:
            logging.error(f"Errore recupero ultimo valore sensore {sensor_type} per {plant_id}: {e}")
            return None
    
    def get_sensor_history(self, plant_id: str, sensor_type: str, hours: int = 24) -> List[Dict[str, Any]]:
        """
        Recupera la cronologia di un sensore per una pianta.
        
        Args:
            plant_id: ID della pianta
            sensor_type: Tipo di sensore (es. "humidity", "temperature")
            hours: Numero di ore di cronologia da recuperare
            
        Returns:
            Lista di dizionari con {timestamp, value, time_formatted}
        """
        try:
            data = self._load_plant_data(plant_id)
            if sensor_type not in data["sensors"]:
                return []
            
            current_time = int(time.time())
            cutoff_time = current_time - (hours * 3600)
            
            sensor_data = data["sensors"][sensor_type]
            filtered_data = [
                entry for entry in sensor_data 
                if entry["timestamp"] >= cutoff_time
            ]
            
            formatted_data = []
            for entry in filtered_data:
                timestamp = entry["timestamp"]
                value = entry["value"]
                
                dt = datetime.fromtimestamp(timestamp)
                time_formatted = dt.strftime("%H:%M")
                
                formatted_data.append({
                    "timestamp": timestamp,
                    "value": value,
                    "time_formatted": time_formatted,
                    "hour": dt.hour,
                    "minute": dt.minute
                })
            
            formatted_data.sort(key=lambda x: x["timestamp"])
            
            logging.info(f"Recuperati {len(formatted_data)} punti per {sensor_type} di {plant_id}")
            return formatted_data
            
        except Exception as e:
            logging.error(f"Errore recupero cronologia sensore {sensor_type} per {plant_id}: {e}")
            return []

    def process_sensor_data_and_evaluate_policies(self, plant_descriptor, sensor_type: str, sensor_value: float, policy_manager):
        """
        Processa i dati del sensore, li salva e valuta le policy.
        
        Args:
            plant_descriptor: PlantDescriptor della pianta
            sensor_type: Tipo di sensore (es. "humidity", "temperature")
            sensor_value: Valore del sensore ricevuto
            policy_manager: PolicyManager per la valutazione delle policy
            
        Returns:
            List[str]: Lista delle azioni eseguite
        """
        try:
            self.save_sensor_data(
                plant_id=plant_descriptor.plant_id,
                sensor_type=sensor_type,
                value=sensor_value,
                species=plant_descriptor.species
            )
            print(f"💾 Dati sensore salvati: {sensor_type} = {sensor_value}")
            
            for sensor in plant_descriptor.sensors:
                if sensor.type == sensor_type:
                    sensor.value = sensor_value
                    break
            
            sensor_values = {}
            for sensor in plant_descriptor.sensors:
                sensor_values[sensor.type] = sensor.value
            
            actions, alerts = policy_manager.evaluate_policies(plant_descriptor, sensor_values)
            
            for alert in alerts:
                print(f"🚨 ALERT per {plant_descriptor.plant_id}: {alert}")
            
            return actions
            
        except Exception as e:
            logging.error(f"Errore processamento dati sensore {sensor_type}: {e}")
            return []

