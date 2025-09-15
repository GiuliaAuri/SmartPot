#!/usr/bin/env python3
"""
JsonManager - Gestione dei file JSON per il salvataggio dei dati delle piante.

Questo modulo gestisce:
- Creazione di file JSON separati per ogni pianta
- Salvataggio dei dati dei sensori con timestamp
- Salvataggio dei dati degli attuatori con timestamp
- Struttura dati organizzata e leggibile
"""

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
    con la struttura:
    {
        "plant_id": "plant_cactus_001",
        "species": "cactus",
        "created_at": "2024-01-01T00:00:00Z",
        "last_updated": "2024-01-01T12:00:00Z",
        "sensors": {
            "humidity": [
                {"value": 65, "timestamp": 1704067200}
            ],
            "temperature": [
                {"value": 25, "timestamp": 1704067200}
            ]
        },
        "actuators": {
            "irrigation": [
                {"action": "start", "timestamp": 1704067200}
            ]
        }
    }
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
                    
                # Gestisce sia struttura lista che dizionario
                if isinstance(data, list) and len(data) > 0:
                    # Struttura lista: prendi il primo elemento
                    plant_data = data[0]
                    # Converte alla nuova struttura
                    return self._convert_old_structure_to_new(plant_data, plant_id)
                elif isinstance(data, dict):
                    # Struttura dizionario: usa direttamente
                    return data
                else:
                    logging.warning(f"Struttura file non riconosciuta in {file_path}")
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
    
    def _convert_old_structure_to_new(self, old_data: Dict[str, Any], plant_id: str) -> Dict[str, Any]:
        """
        Converte la struttura vecchia (lista) alla nuova struttura (dizionario).
        
        Args:
            old_data: Dati nella struttura vecchia
            plant_id: ID della pianta
            
        Returns:
            Dati nella nuova struttura
        """
        now = datetime.now()
        
        # Crea nuova struttura
        new_data = {
            "plant_id": plant_id,
            "species": old_data.get("species", "unknown"),
            "created_at": now.isoformat() + "Z",
            "last_updated": now.isoformat() + "Z",
            "sensors": {},
            "actuators": {}
        }
        
        # Converte sensori dalla struttura vecchia
        if "sensors" in old_data and isinstance(old_data["sensors"], list):
            for sensor in old_data["sensors"]:
                sensor_name = sensor.get("sensor", "unknown")
                device = sensor.get("device", "unknown")
                
                if sensor_name not in new_data["sensors"]:
                    new_data["sensors"][sensor_name] = []
                
                # Converte i valori
                if "values" in sensor and isinstance(sensor["values"], list):
                    for value_entry in sensor["values"]:
                        new_entry = {
                            "value": value_entry.get("value"),
                            "timestamp": int(value_entry.get("timestamp", time.time()))
                        }
                        new_data["sensors"][sensor_name].append(new_entry)
        
        # Converte attuatori dalla struttura vecchia
        if "actuators" in old_data and isinstance(old_data["actuators"], list):
            for actuator in old_data["actuators"]:
                actuator_type = actuator.get("type", "unknown")
                device = actuator.get("device", "unknown")
                
                if actuator_type not in new_data["actuators"]:
                    new_data["actuators"][actuator_type] = []
                
                # Converte i valori
                if "values" in actuator and isinstance(actuator["values"], list):
                    for value_entry in actuator["values"]:
                        # Converte boolean a stringa per le azioni
                        action = "start" if value_entry.get("value", False) else "stop"
                        new_entry = {
                            "action": action,
                            "timestamp": int(value_entry.get("timestamp", time.time()))
                        }
                        new_data["actuators"][actuator_type].append(new_entry)
        
        return new_data
    
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
            # Carica dati esistenti
            data = self._load_plant_data(plant_id)
            
            # Se è un nuovo file, imposta la specie
            if data["species"] == "unknown" and species != "unknown":
                data["species"] = species
            
            # Inizializza sensore se non esiste
            if sensor_type not in data["sensors"]:
                data["sensors"][sensor_type] = []
            
            # Crea nuova entry
            timestamp = int(time.time())
            entry = {
                "value": value,
                "timestamp": timestamp
            }
            
            # Aggiungi entry
            data["sensors"][sensor_type].append(entry)
            
            # Mantieni solo le ultime max_entries entry
            if len(data["sensors"][sensor_type]) > max_entries:
                data["sensors"][sensor_type] = data["sensors"][sensor_type][-max_entries:]
            
            # Salva dati
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
            # Carica dati esistenti
            data = self._load_plant_data(plant_id)
            
            # Se è un nuovo file, imposta la specie
            if data["species"] == "unknown" and species != "unknown":
                data["species"] = species
            
            # Inizializza attuatore se non esiste
            if actuator_type not in data["actuators"]:
                data["actuators"][actuator_type] = []
            
            # Crea nuova entry
            timestamp = int(time.time())
            entry = {
                "action": action,
                "timestamp": timestamp
            }
            
            # Aggiungi entry
            data["actuators"][actuator_type].append(entry)
            
            # Mantieni solo le ultime max_entries entry
            if len(data["actuators"][actuator_type]) > max_entries:
                data["actuators"][actuator_type] = data["actuators"][actuator_type][-max_entries:]
            
            # Salva dati
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
                    plant_id = filename[:-5]  # Rimuovi .json
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

# Test del JsonManager
if __name__ == "__main__":
    # Configura logging
    logging.basicConfig(level=logging.INFO)
    
    # Test del JsonManager
    manager = JsonManager()
    
    # Test salvataggio sensore
    manager.save_sensor_data("test_plant", "humidity", 65.5, "cactus")
    manager.save_sensor_data("test_plant", "temperature", 25.0, "cactus")
    
    # Test salvataggio attuatore
    manager.save_actuator_data("test_plant", "irrigation", "start", "cactus")
    
    # Test recupero dati
    data = manager.get_plant_data("test_plant")
    print("Dati pianta test:")
    print(json.dumps(data, indent=2))
    
    # Test ultimo valore
    last_humidity = manager.get_latest_sensor_value("test_plant", "humidity")
    print(f"Ultima umidità: {last_humidity}")
    
    # Test lista piante
    plants = manager.list_plants()
    print(f"Piante trovate: {plants}")
