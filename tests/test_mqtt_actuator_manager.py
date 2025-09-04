import sys
import os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
import unittest
from unittest.mock import MagicMock, patch
from plants_system.process.mqtt_actuator_manager import MqttActuatorManager
from plants_system.smart_objects.models.plant_descriptor import PlantDescriptor

class TestMqttActuatorManager(unittest.TestCase):
    @patch("process.mqtt_actuator_manager.mqtt.Client")
    def setUp(self, mock_mqtt_client):
        # Mock del client MQTT
        mock_client_instance = MagicMock()
        mock_mqtt_client.return_value = mock_client_instance
        # Crea una pianta di test
        self.plant = PlantDescriptor(species="cactus", plant_id="plant_cactus_001")
        self.manager = MqttActuatorManager(self.plant)
        self.manager.client = mock_client_instance  # Assicura che il mock sia usato

    def test_on_connect_subscribes_topics(self):
        actuator = self.plant.actuators[0]
        self.manager.on_connect(self.manager.client, None, None, 0)
        topic = self.manager.client.subscribe.call_args[0][0]
        self.assertIn(actuator.device, topic)

    def test_send_command_publishes(self):
        actuator = self.plant.actuators[0]
        self.manager.send_command("ON", actuator)
        self.manager.client.publish.assert_called()
        args, kwargs = self.manager.client.publish.call_args
        self.assertIn(actuator.device, args[0])
        self.assertEqual(args[1], "ON")

    def test_on_message_calls_handle_command(self):
        actuator = self.plant.actuators[0]
        actuator.handle_command = MagicMock()
        topic = self.manager.client.publish.call_args[0][0] if self.manager.client.publish.call_args else "test_topic"
        # Simula ricezione messaggio
        with patch("process.mqtt_actuator_manager.MqttConfigurationParameters.build_command_plant_topic", return_value=topic):
            message = MagicMock()
            message.payload.decode.return_value = "ON"
            message.topic = topic
            self.manager.on_message(self.manager.client, None, message)
            actuator.handle_command.assert_called_with("ON")

if __name__ == "__main__":
    unittest.main()