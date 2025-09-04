import sys
import os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
import unittest
from unittest.mock import MagicMock, patch
from process.mqtt_sensor_manager import MqttSensorManager
from model.plant_descriptor import PlantDescriptor

class TestMqttSensorManager(unittest.TestCase):
    @patch("process.mqtt_sensor_manager.mqtt.Client")
    def setUp(self, mock_mqtt_client):
        # Mock del client MQTT
        mock_client_instance = MagicMock()
        mock_mqtt_client.return_value = mock_client_instance
        # Crea una pianta di test
        self.plant = PlantDescriptor(species="cactus", plant_id="plant_cactus_001")
        self.manager = MqttSensorManager(self.plant)
        self.manager.client = mock_client_instance  # Assicura che il mock sia usato

    def test_on_connect_subscribes_topic(self):
        self.manager.on_connect(self.manager.client, None, None, 0)
        self.manager.client.subscribe.assert_called()
        topic = self.manager.client.subscribe.call_args[0][0]
        self.assertIn(self.plant.plant_id, topic)

    def test_publish_telemetry(self):
        # Mock sensors
        for sensor in self.plant.sensors:
            sensor.update = MagicMock()
            sensor.to_json = MagicMock(return_value='{"mock": "data"}')
        self.manager.publish_telemetry()
        self.manager.client.publish.assert_called()
        args, kwargs = self.manager.client.publish.call_args
        self.assertIn(self.plant.plant_id, args[0])
        self.assertEqual(args[1], '{"mock": "data"}')

    def test_on_message_logs(self):
        message = MagicMock()
        message.payload.decode.return_value = "test_payload"
        message.topic = "test/topic"
        with self.assertLogs("sensor", level="INFO"):
            self.manager.on_message(self.manager.client, None, message)

if __name__ == "__main__":
    unittest.main()