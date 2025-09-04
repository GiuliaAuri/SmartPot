import sys
import os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
import unittest
from backend.app import app
from plants_system.smart_objects.resources.factory_plants import PlantFactory
from plants_system.process.client_data_collector import PlantClient

class TestApiTelemetry(unittest.TestCase):
    def setUp(self):
        # Ensure app has plants and client initialized like when running
        plants = PlantFactory.create_plants_from_json("smart_objects/resourses/plants_config.json")
        # Attach plants to module so endpoint can find them
        app.plants = plants
        app.client = PlantClient(plants)
        self.client = app.test_client()

    def test_get_plant_telemetry_success(self):
        response = self.client.get('/api/plants/plant01/telemetry')
        self.assertEqual(response.status_code, 200)
        data = response.get_json()
        self.assertIn("plant_id", data)
        self.assertIn("telemetry", data)
        # Puoi aggiungere altre verifiche sui dati dei sensori

    def test_get_plant_telemetry_not_found(self):
        response = self.client.get('/api/plants/nonexistent/telemetry')
        self.assertEqual(response.status_code, 404)
        data = response.get_json()
        self.assertIn("error", data)

if __name__ == "__main__":
    unittest.main()