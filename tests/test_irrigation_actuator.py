import sys
import os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
import unittest
from smart_objects.actuators.irrigation_actuator import IrrigationActuator

class TestIrrigationActuator(unittest.TestCase):
    def setUp(self):
        self.actuator = IrrigationActuator(plant_id="plant_cactus_001")

    def test_initial_status(self):
        self.assertFalse(self.actuator.status)

    def test_type_and_device(self):
        self.assertEqual(self.actuator.type, "irrigation_actuator")
        self.assertEqual(self.actuator.device, "irrigation_actuator")

    def test_change_status(self):
        self.actuator.change_status()
        self.assertTrue(self.actuator.status)
        self.actuator.change_status()
        self.assertFalse(self.actuator.status)

    def test_handle_command_on(self):
        self.actuator.handle_command("ON")
        self.assertTrue(self.actuator.status)

    def test_handle_command_off(self):
        self.actuator.handle_command("OFF")
        self.assertFalse(self.actuator.status)

if __name__ == "__main__":
    unittest.main()