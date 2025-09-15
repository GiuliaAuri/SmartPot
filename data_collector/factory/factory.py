from data_collector.plant_descriptor import PlantDescriptor

#TODO: aggiungere la creazione della plant descriptor da file json
class Factory:
    """ create the plant descriptor from the json file """
    
    @staticmethod
    def create_plant_descriptor():
        species = "cactus"
        plant_id = "plant_cactus_001"
        plant_descriptor = PlantDescriptor(species, plant_id)
        return [plant_descriptor]
    
    
