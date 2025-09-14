from flask import Flask, jsonify, request
import logging
import os
import sys

# Add the project root to Python path to import factory_plants
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# Import managers
from managers.plant_data_manager import PlantDataManager
from managers.config_manager import ConfigManager

# Import processors
from processors.sensor_processor import SensorDataProcessor
from processors.actuator_processor import ActuatorDataProcessor

# Import routes
from routes.plants import plants_bp
from routes.alerts import alerts_bp
from routes.system import system_bp

# Configurazione Flask
app = Flask(__name__)
from flask_cors import CORS
CORS(app, origins=["http://localhost:3000", "http://127.0.0.1:3000"], 
     methods=["GET", "POST", "PUT", "DELETE", "OPTIONS"])

logging.basicConfig(level=logging.INFO)

# Gestione CORS preflight
@app.before_request
def handle_preflight():
    """
    Gestisce le richieste CORS preflight per permettere chiamate cross-origin.
    
    Questa funzione intercetta le richieste OPTIONS che i browser inviano
    automaticamente prima delle richieste CORS per verificare se il server
    supporta le chiamate cross-origin.
    
    Returns:
        Response: Risposta HTTP con headers CORS appropriati se la richiesta
                 è di tipo OPTIONS, altrimenti None per continuare il normale
                 flusso di elaborazione della richiesta.
    """
    if request.method == "OPTIONS":
        response = jsonify({})
        response.headers.add("Access-Control-Allow-Origin", request.headers.get('Origin', '*'))
        response.headers.add('Access-Control-Allow-Headers', "Content-Type,Authorization")
        response.headers.add('Access-Control-Allow-Methods', "GET,PUT,POST,DELETE,OPTIONS")
        return response

# Inizializzazione managers
config_manager = ConfigManager()
data_manager = PlantDataManager()
sensor_processor = SensorDataProcessor()
actuator_processor = ActuatorDataProcessor()

# Caricamento dati
if data_manager.load_configurations():
    app.plants_data = data_manager.load_plants_data()
else:
    app.plants_data = {}

# Registrazione blueprint
app.register_blueprint(plants_bp)
app.register_blueprint(alerts_bp)
app.register_blueprint(system_bp)

# Avvio applicazione
if __name__ == "__main__":
    server_config = config_manager.get_server_config()
    app.run(
        host=server_config.get("host", "127.0.0.1"),
        port=server_config.get("port", 5000),
        debug=server_config.get("debug", True)
    )