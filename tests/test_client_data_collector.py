import sys
import os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
import unittest
from unittest.mock import MagicMock, patch
from process.client_data_collector import PlantClient
from model.plant_descriptor import PlantDescriptor

class TestPlantClient(unittest.TestCase):
    @patch("process.client_data_collector.MqttSensorManager")
    @patch("process.client_data_collector.MqttActuatorManager")
    def setUp(self, mock_actuator_manager, mock_sensor_manager):
        # Crea una pianta di test
        self.plant = PlantDescriptor(species="cactus", plant_id="plant_cactus_001")
        # Mock dei manager
        mock_sensor_manager.return_value = MagicMock()
        mock_actuator_manager.return_value = MagicMock()
        self.client = PlantClient([self.plant])

    def test_managers_created(self):
        self.assertIn("plant_cactus_001", self.client.sensor_managers)
        self.assertIn("plant_cactus_001", self.client.actuator_managers)

    @patch("process.client_data_collector.MqttActuatorManager")
    def test_send_command(self, mock_actuator_manager):
        actuator = self.plant.actuators[0]
        mock_manager = MagicMock()
        self.client.actuator_managers["plant_cactus_001"] = mock_manager
        self.client.send_command("plant_cactus_001", actuator.device, "ON")
        mock_manager.send_command.assert_called_with("ON", actuator)

    def test_send_command_invalid_plant(self):
        with self.assertLogs(level="ERROR"):
            self.client.send_command("invalid_id", "irrigation_actuator", "ON")

    def test_send_command_invalid_actuator(self):
        with self.assertLogs(level="ERROR"):
            self.client.send_command("plant_cactus_001", "invalid_actuator", "ON")

if __name__ == "__main__":
    unittest.main()