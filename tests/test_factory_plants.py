import sys
import os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
import unittest
import os
from smart_objects.resourses.factory_plants import PlantFactory

class TestPlantFactory(unittest.TestCase):
    def setUp(self):
        # Crea un file JSON temporaneo per il test
        self.test_json = "test_plants_config.json"
        plants_data = [
            {"species": "cactus", "plant_id": "plant_cactus_001"},
            {"species": "orchid", "plant_id": "plant_orchid_001"}
        ]
        with open(self.test_json, "w") as f:
            import json
            json.dump(plants_data, f)

    def tearDown(self):
        # Rimuovi il file JSON temporaneo
        if os.path.exists(self.test_json):
            os.remove(self.test_json)

    def test_create_plants_from_json(self):
        plants = PlantFactory.create_plants_from_json(self.test_json)
        self.assertEqual(len(plants), 2)
        self.assertEqual(plants[0].species, "cactus")
        self.assertEqual(plants[0].plant_id, "plant_cactus_001")
        self.assertEqual(plants[1].species, "orchid")
        self.assertEqual(plants[1].plant_id, "plant_orchid_001")

if __name__ == "__main__":
    unittest.main()