import sys
import os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
import unittest
from device.environment_telemetry import EnvironmentTelemetryData

class TestEnvironmentTelemetryData(unittest.TestCase):
    def setUp(self):
        self.env = EnvironmentTelemetryData(plant_id="plant_cactus_001")

    def test_initial_values(self):
        self.assertEqual(self.env.plant_id, "plant_cactus_001")
        self.assertEqual(self.env.device, "environment_telemetry")
        self.assertIsNotNone(self.env.temperature)
        self.assertIsNotNone(self.env.humidity)
        self.assertIsNotNone(self.env.lightness)
        self.assertIsNotNone(self.env.batteryLevel)

    def test_update_measurements(self):
        old_timestamp = self.env.timestamp
        self.env.update_measurements()
        self.assertTrue(self.env.timestamp >= old_timestamp)

    def test_to_json(self):
        json_str = self.env.to_json()
        self.assertIn("plant_cactus_001", json_str)
        self.assertIn("environment_telemetry", json_str)

if __name__ == "__main__":
    unittest.main()