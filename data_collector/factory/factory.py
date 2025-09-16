import json
import os
from data_collector.plant_descriptor import PlantDescriptor

class Factory:
    """ create the plant descriptor from the json file """
    
    @staticmethod
    def create_plant_descriptor():
        """Legge la configurazione dal file plants_config.json"""
        config_path = os.path.join(os.path.dirname(__file__), "plants_config.json")
        
        try:
            with open(config_path, 'r', encoding='utf-8') as f:
                config = json.load(f)
            
            plant_descriptors = []
            
            for plant_config in config.get("plants", []):
                plant_id = plant_config.get("plant_id")
                species = plant_config.get("species")
                
                if plant_id and species:
                    plant_descriptor = PlantDescriptor(species, plant_id)
                    plant_descriptors.append(plant_descriptor)
                    print(f"✅ Creato plant descriptor: {plant_id} ({species})")
                else:
                    print(f"⚠️ Configurazione pianta incompleta: {plant_config}")
            
            return plant_descriptors
            
        except FileNotFoundError:
            print(f"❌ File di configurazione non trovato: {config_path}")
            # Fallback ai valori di default
            species = "cactus"
            plant_id = "plant_cactus_001"
            plant_descriptor = PlantDescriptor(species, plant_id)
            return [plant_descriptor]
            
        except json.JSONDecodeError as e:
            print(f"❌ Errore parsing JSON: {e}")
            # Fallback ai valori di default
            species = "cactus"
            plant_id = "plant_cactus_001"
            plant_descriptor = PlantDescriptor(species, plant_id)
            return [plant_descriptor]
    
    
