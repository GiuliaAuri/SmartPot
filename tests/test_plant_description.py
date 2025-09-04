import sys
import os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
import unittest
from smart_objects.model.plant_descriptor import PlantDescriptor

class TestPlantDescriptor(unittest.TestCase):
    def setUp(self):
        self.plant = PlantDescriptor(species="cactus", plant_id="plant_cactus_001")

    def test_plant_id_and_species(self):
        self.assertEqual(self.plant.plant_id, "plant_cactus_001")
        self.assertEqual(self.plant.species, "cactus")

    def test_sensors_initialization(self):
        self.assertTrue(len(self.plant.sensors) > 0)

    def test_actuators_initialization(self):
        self.assertTrue(len(self.plant.actuators) > 0)

    def test_to_json(self):
        json_str = self.plant.to_json()
        self.assertIn("plant_cactus_001", json_str)
        self.assertIn("cactus", json_str)

if __name__ == "__main__":
    unittest.main()