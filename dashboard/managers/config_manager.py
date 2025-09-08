import json
import os
import logging


class ConfigManager:
    """Manages application configuration"""
    
    def __init__(self):
        self.config = self.load_config()
    
    def load_config(self):
        """Load configuration from config.json"""
        try:
            config_path = os.path.join(os.path.dirname(__file__), '..', 'config.json')
            with open(config_path, 'r', encoding='utf-8') as f:
                return json.load(f)
        except Exception as e:
            logging.warning(f"Could not load config.json: {e}. Using defaults.")
            return {
                "server": {"host": "127.0.0.1", "port": 5000, "debug": True},
                "update": {"frequency_seconds": 30},
                "data": {"precision": 1}
            }
    
    def get_server_config(self):
        """Get server configuration"""
        return self.config.get("server", {"host": "127.0.0.1", "port": 5000, "debug": True})
    
    def get_update_frequency(self):
        """Get update frequency in seconds"""
        return self.config.get("update", {}).get("frequency_seconds", 30)
    
    def get_data_precision(self):
        """Get data precision (decimal places)"""
        return self.config.get("data", {}).get("precision", 1)
