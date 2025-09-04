import sys
import os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
import unittest
from plants_system.smart_objects.devices.tank_monitoring import TankMonitoring

class TestTankMonitoring(unittest.TestCase):
    def setUp(self):
        self.tank = TankMonitoring(plant_id="plant_cactus_001")

    def test_initial_values(self):
        self.assertEqual(self.tank.plant_id, "plant_cactus_001")
        self.assertEqual(self.tank.device, "tank_monitoring")
        self.assertIsNotNone(self.tank.level_tank)

    def test_update_measurements(self):
        old_timestamp = self.tank.timestamp
        self.tank.update_measurements()
        self.assertTrue(self.tank.timestamp >= old_timestamp)

    def test_to_json(self):
        json_str = self.tank.to_json()
        self.assertIn("plant_cactus_001", json_str)
        self.assertIn("tank_monitoring", json_str)

if __name__ == "__main__":
    unittest.main()