"""
Server REST API per il frontend web app.
Legge i dati dai file JSON del data_collector e li espone via REST API.
"""

import os
import sys

# Aggiungi il path per importare i moduli del progetto PRIMA degli import
project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
sys.path.insert(0, project_root)

import json
import time
from datetime import datetime, timedelta
from typing import Dict, List, Any, Optional
from flask import Flask, jsonify, request
from flask_cors import CORS
import logging
from data_collector.data_collector_producer import DataCollectorProducer
from data_collector.plant_descriptor import PlantDescriptor
from data_collector.json_manager import JsonManager

# Configurazione logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = Flask(__name__)
CORS(app)  # Abilita CORS per il frontend

# Configurazione
PLANTS_LOG_PATH = "cloud_simulator/plants_log"
DEFAULT_POLLING_INTERVAL = 5  # secondi

class PlantDataService:
    """Servizio per leggere e processare i dati delle piante usando JsonManager."""
    
    def __init__(self, plants_log_path: str):
        self.json_manager = JsonManager(base_path=plants_log_path)
    
    def get_all_plants_data(self) -> List[Dict[str, Any]]:
        """Legge tutti i dati delle piante usando JsonManager."""
        plants_data = []
        
        try:
            # Ottieni lista delle piante da JsonManager
            plant_ids = self.json_manager.list_plants()
            
            for plant_id in plant_ids:
                plant_data = self._load_plant_data(plant_id)
                if plant_data:
                    plants_data.append(plant_data)
            
            logger.info(f"Caricati dati per {len(plants_data)} piante")
            return plants_data
            
        except Exception as e:
            logger.error(f"Errore nel caricamento dati piante: {e}")
            return []
    
    def _load_plant_data(self, plant_id: str) -> Optional[Dict[str, Any]]:
        """Carica i dati di una singola pianta usando JsonManager."""
        try:
            # Usa JsonManager per caricare i dati raw
            raw_data = self.json_manager.get_plant_data(plant_id)
            
            if not raw_data:
                logger.warning(f"Pianta {plant_id} non trovata")
                return None
            
            # Processa i dati per il frontend
            return self._process_plant_data_for_frontend(plant_id, raw_data)
            
        except Exception as e:
            logger.error(f"Errore nel caricamento pianta {plant_id}: {e}")
            return None
    
    def _process_plant_data_for_frontend(self, plant_id: str, data: Dict[str, Any]) -> Dict[str, Any]:
        """Processa i dati della pianta per il formato richiesto dal frontend."""
        
        # Gestisci solo il formato standard (dizionario)
        if not isinstance(data, dict):
            logger.warning(f"Formato dati non supportato per {plant_id}: {type(data)}")
            return None
        
        # Estrai dati dal formato standard
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
    
    def _send_mqtt_command(self, plant_id: str, actuator_type: str, command: str) -> bool:
        """Invia un comando MQTT all'attuatore usando DataCollectorProducer."""
        try:
            # Crea un PlantDescriptor temporaneo per il producer
            plant_descriptor = PlantDescriptor(species="unknown", plant_id=plant_id)
            
            # Crea il producer con il comando usando il path da JsonManager
            producer = DataCollectorProducer(
                plant_descriptor=plant_descriptor,
                command=f"{command} {actuator_type}",
                json_path=self.json_manager.base_path
            )
            
            # Esegue il comando (pubblica MQTT e salva nel JSON)
            producer.run()
            
            logger.info(f"Comando MQTT inviato tramite DataCollectorProducer: {actuator_type} = {command}")
            return True
            
        except Exception as e:
            logger.error(f"Errore invio comando MQTT {actuator_type}: {e}")
            return False
    
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
    
# Funzioni di supporto
def convert_action_to_simple_command(action: str) -> str:
    """Converte un'azione complessa in comando semplice."""
    action_lower = action.lower()
    
    if action_lower in ['deactivate', 'stop', 'off']:
        return 'stop'
    elif action_lower in ['activate', 'start', 'on']:
        return 'start'
    else:
        return action_lower

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

@app.route('/api/plants/<plant_id>/actuators/<actuator_type>', methods=['POST'])
def control_actuator(plant_id: str, actuator_type: str):
    """Endpoint per controllare manualmente un attuatore."""
    try:
        # Leggi il payload della richiesta
        data = request.get_json()
        if not data or 'action' not in data:
            return jsonify({"error": "Payload mancante o formato non valido"}), 400
        
        action = data['action'].lower()
        
        # Valida l'azione
        valid_actions = ['start', 'stop', 'on', 'off', 'activate', 'deactivate']
        if action not in valid_actions:
            return jsonify({"error": f"Azione non valida. Valori accettati: {valid_actions}"}), 400
        
        # Verifica che la pianta esista
        plant_data = plant_service._load_plant_data(plant_id)
        if not plant_data:
            return jsonify({"error": f"Pianta {plant_id} non trovata"}), 404
        
        # Converti l'azione in comando semplice
        simple_command = convert_action_to_simple_command(action)
        
        # Invia comando MQTT all'attuatore (che salva anche nel JSON)
        mqtt_success = plant_service._send_mqtt_command(plant_id, actuator_type, simple_command)
        
        return jsonify({
            "success": True,
            "message": f"Comando {simple_command} inviato all'attuatore {actuator_type}",
            "plant_id": plant_id,
            "actuator_type": actuator_type,
            "action": simple_command,
            "mqtt_sent": mqtt_success,
            "timestamp": datetime.now().isoformat()
        })
        
    except Exception as e:
        logger.error(f"Errore nell'endpoint POST /api/plants/{plant_id}/actuators/{actuator_type}: {e}")
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
