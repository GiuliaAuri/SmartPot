import sys
import os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
import unittest
from unittest.mock import MagicMock, patch
from process.plants_server import PlantServer
from model.plant_descriptor import PlantDescriptor

class TestPlantServer(unittest.TestCase):
    @patch("process.plants_server.MqttSensorManager")
    @patch("process.plants_server.MqttActuatorManager")
    def setUp(self, mock_actuator_manager, mock_sensor_manager):
        # Crea una pianta di test
        self.plant = PlantDescriptor(species="cactus", plant_id="plant_cactus_001")
        # Mock dei manager
        mock_sensor_manager.return_value = MagicMock()
        mock_actuator_manager.return_value = MagicMock()
        self.server = PlantServer([self.plant])

    def test_managers_created(self):
        self.assertIn("plant_cactus_001", self.server.sensor_managers)
        self.assertIn("plant_cactus_001", self.server.actuator_managers)

    def test_run_calls_publish_telemetry_and_policy(self):
        self.server.sensor_managers["plant_cactus_001"].publish_telemetry = MagicMock()
        self.server.policy_manager = MagicMock()
        # Simula un solo ciclo del while
        with patch("time.sleep", return_value=None), patch("builtins.input", side_effect=KeyboardInterrupt):
            try:
                self.server.run(interval=0.1)
            except KeyboardInterrupt:
                pass
        self.server.sensor_managers["plant_cactus_001"].publish_telemetry.assert_called()
        self.server.policy_manager.evaluate.assert_called_with(self.plant)

    def test_stop_calls_managers(self):
        self.server.sensor_managers["plant_cactus_001"].stop = MagicMock()
        self.server.actuator_managers["plant_cactus_001"].stop = MagicMock()
        self.server.stop()
        self.server.sensor_managers["plant_cactus_001"].stop.assert_called()
        self.server.actuator_managers["plant_cactus_001"].stop.assert_called()

if __name__ == "__main__":
    unittest.main()