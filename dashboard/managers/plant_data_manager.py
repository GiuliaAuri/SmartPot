import json
import os
import logging


class PlantDataManager:
    """Manages plant data loading and processing"""
    
    def __init__(self):
        self.project_root = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
        self.plants_config = None
        self.plants_data = {}
        
    def load_configurations(self):
        """Load plants configuration file"""
        try:
            # Load plants configuration
            plants_config_path = os.path.join(self.project_root, 'cloud_simulator', 'plants.json')
            with open(plants_config_path, 'r', encoding='utf-8') as f:
                self.plants_config = json.load(f)
            
            logging.info("Plants configuration loaded successfully")
            return True
        except Exception as e:
            logging.error(f"Error loading plants configuration: {e}")
            return False
    
    def load_plants_data(self):
        """Load plants data from log files - only plants that have actual log files"""
        if not self.plants_config:
            return {}
        
        plants_data = {}
        # Handle both old format (list) and new format ({"plants": [...]})
        plant_configs = self.plants_config if isinstance(self.plants_config, list) else self.plants_config.get("plants", [])
        
        # First, get all available log files
        log_dir = os.path.join(self.project_root, 'cloud_simulator', 'plants_log')
        available_log_files = set()
        if os.path.exists(log_dir):
            for file in os.listdir(log_dir):
                if file.endswith('.json'):
                    plant_id = file[:-5]  # Remove .json extension
                    available_log_files.add(plant_id)
        
        # Only process plants that have log files
        for plant_config in plant_configs:
            plant_id = plant_config['plant_id']
            
            if plant_id in available_log_files:
                # Load plant-specific data
                log_file = os.path.join(log_dir, f'{plant_id}.json')
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
                    logging.info(f"Loaded data for plant {plant_id}")
                except json.JSONDecodeError as e:
                    logging.warning(f"JSON decode error in {log_file}: {e}. Using config only.")
                    plants_data[plant_id] = plant_config
            else:
                logging.info(f"Skipping plant {plant_id} - no log file found")
        
        self.plants_data = plants_data
        logging.info(f"Successfully loaded data for {len(plants_data)} plants")
        return plants_data