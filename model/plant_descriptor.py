import json


class PlantDescriptor:

    def __init__(self, uuid, species):
        self.uuid = uuid
        self.species = species
        #TODO aggiungere lista di sensori e attuatori

    def to_json(self):
        return json.dumps(self, default=lambda o: o.__dict__)