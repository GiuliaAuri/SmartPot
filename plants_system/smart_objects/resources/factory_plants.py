import json
import os
import logging
from plants_system.smart_objects.models.plant_descriptor import PlantDescriptor
from plants_system.smart_objects.sensors.temperature_sensor import TemperatureSensor
from plants_system.smart_objects.sensors.humidity_sensor import HumiditySensor
from plants_system.smart_objects.devices.tank_monitoring import TankMonitoring
from plants_system.smart_objects.devices.water_metering import WaterMetering
from plants_system.smart_objects.devices.environment_telemetry import EnvironmentTelemetryData
from plants_system.smart_objects.models.SwitchActuator import SwitchActuator
from plants_system.smart_objects.resources.factory_config import FactoryConfig

logger = logging.getLogger("plant_factory")

class PlantFactory:
    """
    Factory per la creazione di piante da file JSON.
    
    Questa classe permette di creare oggetti PlantDescriptor da file JSON,
    contenenti informazioni base sulla pianta come nome e tipo.
    """
    
    @staticmethod
    def create_plants_from_json(json_path=None):
        """
        Crea oggetti PlantDescriptor dal file plants_config.json.
        
        Args:
            json_path: Percorso al file JSON (opzionale, usa plants_config.json se non specificato)
        """
        # Se non viene specificato un percorso, usa il file di configurazione standard
        if json_path is None:
            json_path = os.path.join(os.path.dirname(__file__), 'plants_config.json')
        
        try:
            with open(json_path, "r", encoding='utf-8') as f:
                config_data = json.load(f)
        except Exception as e:
            logger.error(f"Errore nel caricamento del file {json_path}: {e}")
            return []
        
        plants = []
        for plant_config in config_data.get("plants", []):
            try:
                plant = PlantFactory._create_plant_from_config(plant_config)
                plants.append(plant)
                logger.info(f"Pianta {plant_config.get('plant_id')} creata con successo")
            except Exception as e:
                logger.error(f"Errore nella creazione della pianta {plant_config.get('plant_id', 'unknown')}: {e}")
        
        logger.info(f"Create {len(plants)} piante dal file {json_path}")
        return plants

    @staticmethod
    def _create_plant_from_config(plant_config):
        """
        Crea un PlantDescriptor da una configurazione di pianta.
        
        Args:
            plant_config: Dizionario con la configurazione della pianta
            
        Returns:
            PlantDescriptor: Oggetto pianta creato
        """
        plant_id = plant_config["plant_id"]
        species = plant_config["species"]

        # Crea i dispositivi basandosi sulla configurazione
        devices = []
        
        # Verifica quali dispositivi sono abilitati nella configurazione
        device_configs = plant_config.get("devices", {})
        
        # Crea EnvironmentTelemetryData se abilitato
        if device_configs.get("environment_telemetry", {}).get("enabled", True):
            devices.append(EnvironmentTelemetryData(plant_id))
        
        # Crea TankMonitoring se abilitato
        if device_configs.get("tank_monitoring", {}).get("enabled", True):
            devices.append(TankMonitoring(plant_id))
        
        # Crea WaterMetering se abilitato
        if device_configs.get("water_metering", {}).get("enabled", True):
            devices.append(WaterMetering(plant_id))

        return PlantDescriptor(
            species=species,
            plant_id=plant_id,
            devices=devices
        )
