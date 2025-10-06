import json
import os
from data_collector.plant_descriptor import PlantDescriptor
FILEPATH = "plants_config.json"
class Factory:
    """ create the plant descriptor from the json file """
    
    @staticmethod
    def create_plant_descriptor():
        """Legge la configurazione dal file plants_config.json"""
        config_path = os.path.join(os.path.dirname(__file__), FILEPATH)
        
        try:
            with open(config_path, 'r', encoding='utf-8') as f:
                config = json.load(f)
            
            plant_descriptors = []
            
            for plant_config in config.get("plants", []):
                plant_id = plant_config.get("plant_id")
                species = plant_config.get("species")
                
                if plant_id and species:
                    
                    sensor_config = None
                    sensors_config = plant_config.get("sensors", [])
                    if sensors_config and len(sensors_config) > 0:
                        sensor_config = sensors_config[0].get("humidity")
                    
                    plant_descriptor = PlantDescriptor(species, plant_id, sensor_config=sensor_config)
                    plant_descriptors.append(plant_descriptor)
                    print(f"✅ Creato plant descriptor: {plant_id} ({species})")
                    if sensor_config:
                        print(f"   📊 Sensore umidità: min={sensor_config.get('min_value')}, max={sensor_config.get('max_value')}")
                else:
                    print(f"⚠️ Configurazione pianta incompleta: {plant_config}")
            
            return plant_descriptors
            
        except FileNotFoundError:
            print(f"❌ File di configurazione non trovato: {config_path}")
            species = "cactus"
            plant_id = "plant_cactus_001"
            plant_descriptor = PlantDescriptor(species, plant_id)
            return [plant_descriptor]
            
        except json.JSONDecodeError as e:
            print(f"❌ Errore parsing JSON: {e}")
            species = "cactus"
            plant_id = "plant_cactus_001"
            plant_descriptor = PlantDescriptor(species, plant_id)
            return [plant_descriptor]
    
    
