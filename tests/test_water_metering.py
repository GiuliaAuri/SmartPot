import sys
import os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
import unittest
from device.water_metering import WaterMetering

class TestWaterMetering(unittest.TestCase):
    def setUp(self):
        self.meter = WaterMetering(plant_id="plant_cactus_001")

    def test_initial_values(self):
        self.assertEqual(self.meter.plant_id, "plant_cactus_001")
        self.assertEqual(self.meter.device, "water_metering")
        self.assertIsNotNone(self.meter.water_flow)
        self.assertIsNotNone(self.meter.irrigation)

    def test_update_measurements(self):
        old_timestamp = self.meter.timestamp
        self.meter.update_measurements()
        self.assertTrue(self.meter.timestamp >= old_timestamp)

    def test_to_json(self):
        json_str = self.meter.to_json()
        self.assertIn("plant_cactus_001", json_str)
        self.assertIn("water_metering", json_str)

if __name__ == "__main__":
    unittest.main()