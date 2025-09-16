#!/usr/bin/env python3
"""
Server REST API per il frontend web app.
Legge i dati dai file JSON del data_collector e li espone via REST API.
"""

import os
import sys
import json
import time
from datetime import datetime, timedelta
from typing import Dict, List, Any, Optional
from flask import Flask, jsonify, request
from flask_cors import CORS
import logging

# Aggiungi il path per importare i moduli del progetto
project_root = os.path.abspath(os.path.dirname(__file__))
sys.path.insert(0, project_root)

# Configurazione logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = Flask(__name__)
CORS(app)  # Abilita CORS per il frontend

# Configurazione
PLANTS_LOG_PATH = "cloud_simulator/plants_log"
DEFAULT_POLLING_INTERVAL = 5  # secondi

class PlantDataService:
    """Servizio per leggere e processare i dati delle piante dai file JSON."""
    
    def __init__(self, plants_log_path: str):
        self.plants_log_path = plants_log_path
        self._ensure_directory_exists()
    
    def _ensure_directory_exists(self):
        """Assicura che la directory dei log esista."""
        if not os.path.exists(self.plants_log_path):
            os.makedirs(self.plants_log_path)
            logger.info(f"Creata directory: {self.plants_log_path}")
    
    def get_all_plants_data(self) -> List[Dict[str, Any]]:
        """Legge tutti i dati delle piante dai file JSON."""
        plants_data = []
        
        try:
            # Scansiona tutti i file JSON nella directory
            for filename in os.listdir(self.plants_log_path):
                if filename.endswith('.json'):
                    plant_id = filename.replace('.json', '')
                    plant_data = self._load_plant_data(plant_id)
                    if plant_data:
                        plants_data.append(plant_data)
            
            logger.info(f"Caricati dati per {len(plants_data)} piante")
            return plants_data
            
        except Exception as e:
            logger.error(f"Errore nel caricamento dati piante: {e}")
            return []
    
    def _load_plant_data(self, plant_id: str) -> Optional[Dict[str, Any]]:
        """Carica i dati di una singola pianta dal file JSON."""
        file_path = os.path.join(self.plants_log_path, f"{plant_id}.json")
        
        try:
            if not os.path.exists(file_path):
                logger.warning(f"File non trovato: {file_path}")
                return None
            
            with open(file_path, 'r', encoding='utf-8') as f:
                raw_data = json.load(f)
            
            # Gestisci formato vecchio (lista) e nuovo (dizionario)
            if isinstance(raw_data, list) and len(raw_data) > 0:
                data = raw_data[0]  # Prendi il primo elemento della lista
                logger.info(f"Convertito formato vecchio per {plant_id}")
            elif isinstance(raw_data, dict):
                data = raw_data
            else:
                logger.warning(f"Formato dati non riconosciuto per {plant_id}")
                return None
            
            # Processa i dati per il frontend
            return self._process_plant_data_for_frontend(plant_id, data)
            
        except Exception as e:
            logger.error(f"Errore nel caricamento file {file_path}: {e}")
            return None
    
    def _process_plant_data_for_frontend(self, plant_id: str, data: Dict[str, Any]) -> Dict[str, Any]:
        """Processa i dati della pianta per il formato richiesto dal frontend."""
        
        # Gestisci diversi formati di dati
        if isinstance(data, list) and len(data) > 0:
            # Formato vecchio: lista con primo elemento che contiene i dati
            plant_info = data[0]
            species = plant_info.get("species", plant_info.get("type", "unknown"))
            last_updated = plant_info.get("last_updated", "")
            
            # Gestisci formato sensori come lista
            sensors_list = plant_info.get("sensors", [])
            sensors_data = self._convert_sensors_list_to_dict(sensors_list)
            
            # Gestisci formato attuatori come lista
            actuators_list = plant_info.get("actuators", [])
            actuators_data = self._convert_actuators_list_to_dict(actuators_list)
        else:
            # Formato nuovo: dizionario diretto
            species = data.get("species", "unknown")
            last_updated = data.get("last_updated", "")
            sensors_data = data.get("sensors", {})
            actuators_data = data.get("actuators", {})
        
        # Calcola umidità del suolo (humidity sensor)
        soil_moisture = self._get_latest_sensor_value(sensors_data, "humidity", 50)
        
        # Determina se l'irrigazione è attiva
        is_watering = self._is_irrigation_active(actuators_data)
        
        # Calcola ultima irrigazione
        last_watered = self._get_last_watering_time(actuators_data)
        
        return {
            "id": plant_id,
            "name": f"{species.title()} ({plant_id})",
            "type": species,
            "soilMoisture": soil_moisture,
            "isWatering": is_watering,
            "lastWatered": last_watered,
            "lastUpdated": last_updated,
            "sensors": self._format_sensors_data(sensors_data),
            "actuators": self._format_actuators_data(actuators_data)
        }
    
    def _get_latest_sensor_value(self, sensors_data: Dict, sensor_type: str, default_value: float) -> float:
        """Ottiene l'ultimo valore di un sensore."""
        sensor_entries = sensors_data.get(sensor_type, [])
        if sensor_entries and len(sensor_entries) > 0:
            return float(sensor_entries[-1].get("value", default_value))
        return default_value
    
    def _is_irrigation_active(self, actuators_data: Dict) -> bool:
        """Determina se l'irrigazione è attualmente attiva."""
        irrigation_entries = actuators_data.get("irrigation", [])
        if irrigation_entries and len(irrigation_entries) > 0:
            last_action = irrigation_entries[-1].get("action", "")
            return last_action.lower() in ["start", "on", "activate"]
        return False
    
    def _get_last_watering_time(self, actuators_data: Dict) -> str:
        """Calcola il tempo dell'ultima irrigazione."""
        irrigation_entries = actuators_data.get("irrigation", [])
        if irrigation_entries and len(irrigation_entries) > 0:
            last_timestamp = irrigation_entries[-1].get("timestamp", 0)
            if last_timestamp:
                last_time = datetime.fromtimestamp(last_timestamp)
                now = datetime.now()
                diff = now - last_time
                
                if diff.total_seconds() < 60:
                    return f"{int(diff.total_seconds())} secondi fa"
                elif diff.total_seconds() < 3600:
                    return f"{int(diff.total_seconds() / 60)} minuti fa"
                else:
                    return f"{int(diff.total_seconds() / 3600)} ore fa"
        
        return "Mai"
    
    def _format_sensors_data(self, sensors_data: Dict) -> Dict[str, Any]:
        """Formatta i dati dei sensori per il frontend."""
        formatted = {}
        for sensor_type, entries in sensors_data.items():
            if entries and len(entries) > 0:
                latest_entry = entries[-1]
                formatted[sensor_type] = {
                    "value": latest_entry.get("value", 0),
                    "timestamp": latest_entry.get("timestamp", 0),
                    "history": entries[-10:] if len(entries) > 10 else entries  # Ultimi 10 valori
                }
        return formatted
    
    def _convert_sensors_list_to_dict(self, sensors_list: List[Dict]) -> Dict[str, List[Dict]]:
        """Converte la lista di sensori in formato dizionario."""
        sensors_dict = {}
        for sensor_info in sensors_list:
            sensor_type = sensor_info.get("sensor", "unknown")
            values = sensor_info.get("values", [])
            # Converte i valori nel formato atteso
            converted_values = []
            for value_entry in values:
                converted_values.append({
                    "value": value_entry.get("value", 0),
                    "timestamp": int(value_entry.get("timestamp", 0))
                })
            sensors_dict[sensor_type] = converted_values
        return sensors_dict
    
    def _convert_actuators_list_to_dict(self, actuators_list: List[Dict]) -> Dict[str, List[Dict]]:
        """Converte la lista di attuatori in formato dizionario."""
        actuators_dict = {}
        for actuator_info in actuators_list:
            actuator_type = actuator_info.get("actuator", "unknown")
            values = actuator_info.get("values", [])
            # Converte i valori nel formato atteso
            converted_values = []
            for value_entry in values:
                converted_values.append({
                    "action": value_entry.get("action", ""),
                    "timestamp": int(value_entry.get("timestamp", 0))
                })
            actuators_dict[actuator_type] = converted_values
        return actuators_dict
    
    def _format_actuators_data(self, actuators_data: Dict) -> Dict[str, Any]:
        """Formatta i dati degli attuatori per il frontend."""
        formatted = {}
        for actuator_type, entries in actuators_data.items():
            if entries and len(entries) > 0:
                latest_entry = entries[-1]
                formatted[actuator_type] = {
                    "action": latest_entry.get("action", ""),
                    "timestamp": latest_entry.get("timestamp", 0),
                    "history": entries[-10:] if len(entries) > 10 else entries  # Ultimi 10 valori
                }
        return formatted

# Inizializza il servizio
plant_service = PlantDataService(PLANTS_LOG_PATH)

@app.route('/api/plants', methods=['GET'])
def get_all_plants():
    """Endpoint per ottenere tutti i dati delle piante."""
    try:
        plants_data = plant_service.get_all_plants_data()
        
        # Se non ci sono dati, restituisci dati di esempio
        if not plants_data:
            logger.warning("Nessun dato pianta trovato, restituisco dati di esempio")
            plants_data = [
                {
                    "id": "plant_cactus_001",
                    "name": "Cactus (plant_cactus_001)",
                    "type": "cactus",
                    "soilMoisture": 75,
                    "isWatering": False,
                    "lastWatered": "Nessun dato disponibile",
                    "lastUpdated": datetime.now().isoformat(),
                    "sensors": {},
                    "actuators": {}
                }
            ]
        
        return jsonify(plants_data)
        
    except Exception as e:
        logger.error(f"Errore nell'endpoint /api/plants: {e}")
        return jsonify({"error": str(e)}), 500

@app.route('/api/plants/<plant_id>', methods=['GET'])
def get_plant_by_id(plant_id: str):
    """Endpoint per ottenere i dati di una singola pianta."""
    try:
        plant_data = plant_service._load_plant_data(plant_id)
        
        if not plant_data:
            return jsonify({"error": f"Pianta {plant_id} non trovata"}), 404
        
        return jsonify(plant_data)
        
    except Exception as e:
        logger.error(f"Errore nell'endpoint /api/plants/{plant_id}: {e}")
        return jsonify({"error": str(e)}), 500

@app.route('/api/health', methods=['GET'])
def health_check():
    """Endpoint per il controllo dello stato del server."""
    return jsonify({
        "status": "healthy",
        "timestamp": datetime.now().isoformat(),
        "plants_log_path": PLANTS_LOG_PATH,
        "plants_count": len(plant_service.get_all_plants_data())
    })

@app.route('/api/stats', methods=['GET'])
def get_stats():
    """Endpoint per ottenere statistiche del sistema."""
    try:
        plants_data = plant_service.get_all_plants_data()
        
        stats = {
            "total_plants": len(plants_data),
            "active_irrigation": sum(1 for plant in plants_data if plant.get("isWatering", False)),
            "avg_soil_moisture": sum(plant.get("soilMoisture", 0) for plant in plants_data) / len(plants_data) if plants_data else 0,
            "last_update": datetime.now().isoformat()
        }
        
        return jsonify(stats)
        
    except Exception as e:
        logger.error(f"Errore nell'endpoint /api/stats: {e}")
        return jsonify({"error": str(e)}), 500

if __name__ == "__main__":
    print("🌐 Avvio Web API Server...")
    print(f"📁 Plants log path: {PLANTS_LOG_PATH}")
    print(f"🔗 API Base URL: http://localhost:5000/api")
    print(f"📊 Endpoints disponibili:")
    print(f"   - GET /api/plants - Tutte le piante")
    print(f"   - GET /api/plants/<id> - Pianta specifica")
    print(f"   - GET /api/health - Stato server")
    print(f"   - GET /api/stats - Statistiche sistema")
    print()
    
    # Verifica che la directory esista
    if not os.path.exists(PLANTS_LOG_PATH):
        print(f"⚠️  Directory {PLANTS_LOG_PATH} non trovata!")
        print("   Assicurati che il data_collector sia in esecuzione.")
        print()
    
    app.run(host='0.0.0.0', port=5000, debug=True)
