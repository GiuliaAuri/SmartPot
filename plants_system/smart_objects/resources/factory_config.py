import json
import os
import logging

logger = logging.getLogger("config_manager")

class FactoryConfig:
    """
    Manager per la gestione delle configurazioni delle piante.
    
    Questa classe gestisce il caricamento e l'accesso alle configurazioni
    delle piante dal file JSON, evitando import circolari.
    """
    
    # Cache per le configurazioni caricate
    _config_cache = None
    _config_path = None
    
    @staticmethod
    def _load_config_file():
        """Carica il file di configurazione delle piante"""
        if FactoryConfig._config_cache is not None:
            return FactoryConfig._config_cache
            
        try:
            # Percorso al file di configurazione
            config_path = os.path.join(
                os.path.dirname(__file__),
                'plants_config.json'
            )
            
            with open(config_path, 'r', encoding='utf-8') as f:
                FactoryConfig._config_cache = json.load(f)
                FactoryConfig._config_path = config_path
                logger.info(f"Configurazione caricata da {config_path}")
                return FactoryConfig._config_cache
                
        except Exception as e:
            logger.error(f"Errore nel caricamento della configurazione: {e}")
            return {}
    
    @staticmethod
    def get_plant_config(plant_id):
        """Ottiene la configurazione per una specifica pianta"""
        config_data = FactoryConfig._load_config_file()
        
        for plant in config_data.get('plants', []):
            if plant.get('plant_id') == plant_id:
                return plant
        
        logger.warning(f"Nessuna configurazione trovata per la pianta {plant_id}")
        return {}
    
    @staticmethod
    def get_device_config(plant_id, device_name):
        """Ottiene la configurazione per un dispositivo specifico"""
        plant_config = FactoryConfig.get_plant_config(plant_id)
        return plant_config.get('devices', {}).get(device_name, {})
    
    @staticmethod
    def get_sensor_config(plant_id, device_name, sensor_type):
        """Ottiene la configurazione per un sensore specifico"""
        device_config = FactoryConfig.get_device_config(plant_id, device_name)
        sensors_config = device_config.get('sensors', {})
        return sensors_config.get(sensor_type, {})
    
    @staticmethod
    def get_actuator_config(plant_id, device_name, actuator_type):
        """Ottiene la configurazione per un attuatore specifico"""
        device_config = FactoryConfig.get_device_config(plant_id, device_name)
        actuators_config = device_config.get('actuators', {})
        return actuators_config.get(actuator_type, {})
