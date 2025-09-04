import sys
import os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
import unittest
from app import app

class TestApiTelemetry(unittest.TestCase):
    def setUp(self):
        self.client = app.test_client()
        # Assicura che ci sia almeno una pianta per il test
        if not app.plants:
            from smart_objects.resourses.factory_plants import PlantFactory
            app.plants = PlantFactory.create_plants_from_json("smart_objects/resourses/plants_config.json")

    def test_get_plant_telemetry_success(self):
        # Usa il primo plant_id disponibile
        plant_id = app.plants[0].plant_id
        response = self.client.get(f"/api/plants/{plant_id}/telemetry")
        self.assertEqual(response.status_code, 200)
        data = response.get_json()
        self.assertIn("telemetry", data)
        self.assertEqual(data["plant_id"], plant_id)

    def test_get_plant_telemetry_not_found(self):
        response = self.client.get("/api/plants/nonexistent/telemetry")
        self.assertEqual(response.status_code, 404)
        data = response.get_json()
        self.assertIn("error", data)
        self.assertEqual(data["error"], "Plant not found")

        def test_post_actuator_command_success(self):
            # Usa il primo plant_id e actuator disponibili
            plant = app.plants[0]
            actuator = plant.actuators[0]
            response = self.client.post(f"/api/plants/{plant.plant_id}/actuators/{actuator.device}/command",
                                        json={"command": "ON"})
            self.assertEqual(response.status_code, 200)
            data = response.get_json()
            self.assertEqual(data["plant_id"], plant.plant_id)
            self.assertEqual(data["actuator"], actuator.device)
            self.assertEqual(data["command"], "ON")
            self.assertIn(data["status"], ["ON", "OFF"])  # dipende dall'implementazione

        def test_post_actuator_command_not_found(self):
            # actuator inesistente
            plant = app.plants[0]
            response = self.client.post(f"/api/plants/{plant.plant_id}/actuators/nonexistent_actuator/command",
                                        json={"command": "ON"})
            self.assertEqual(response.status_code, 404)
            data = response.get_json()
            self.assertIn("error", data)
            self.assertEqual(data["error"], "Actuator not found")

        def test_post_actuator_command_missing_command(self):
            # comando mancante
            plant = app.plants[0]
            actuator = plant.actuators[0]
            response = self.client.post(f"/api/plants/{plant.plant_id}/actuators/{actuator.device}/command",
                                        json={})
            self.assertEqual(response.status_code, 400)
            data = response.get_json()
            self.assertIn("error", data)
            self.assertEqual(data["error"], "No command provided")

if __name__ == "__main__":
    unittest.main()
