import json
import os
import logging


class PlantDataManager:
    """Manages plant data loading and processing"""
    
    def __init__(self):
        self.project_root = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
        self.plants_config = None
        self.policies_config = None
        self.plants_data = {}
        
    def load_configurations(self):
        """Load all configuration files"""
        try:
            # Load plants configuration
            plants_config_path = os.path.join(self.project_root, 'cloud_simulator', 'plants.json')
            with open(plants_config_path, 'r', encoding='utf-8') as f:
                self.plants_config = json.load(f)
            
            # Load policies configuration
            policies_config_path = os.path.join(self.project_root, 'plants_system', 'smart_objects', 'resources', 'policies_conf.json')
            with open(policies_config_path, 'r', encoding='utf-8') as f:
                self.policies_config = json.load(f)
            
            logging.info("Configuration files loaded successfully")
            return True
        except Exception as e:
            logging.error(f"Error loading configurations: {e}")
            return False
    
    def load_plants_data(self):
        """Load all plants data from log files"""
        if not self.plants_config:
            return {}
        
        plants_data = {}
        for plant_config in self.plants_config:
            plant_id = plant_config['plant_id']
            
            # Load plant-specific data
            log_file = os.path.join(self.project_root, 'cloud_simulator', 'plants_log', f'{plant_id}.json')
            if os.path.exists(log_file):
                try:
                    with open(log_file, 'r', encoding='utf-8') as f:
                        plant_log_data = json.load(f)
                    
                    # Extract the first (and only) plant data from the array
                    if isinstance(plant_log_data, list) and len(plant_log_data) > 0:
                        plant_log = plant_log_data[0]
                    else:
                        plant_log = plant_log_data
                    
                    # Merge config and log data
                    plants_data[plant_id] = {
                        **plant_config,
                        **plant_log
                    }
                except json.JSONDecodeError as e:
                    logging.warning(f"JSON decode error in {log_file}: {e}. Using config only.")
                    plants_data[plant_id] = plant_config
            else:
                logging.warning(f"Log file not found for plant {plant_id}")
                plants_data[plant_id] = plant_config
        
        self.plants_data = plants_data
        logging.info(f"Successfully loaded data for {len(plants_data)} plants")
        return plants_data
