import sys
import os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
import unittest
from unittest.mock import MagicMock
from process.mqtt_sensor_manager import MqttSensorManager
from process.mqtt_actuator_manager import MqttActuatorManager
from smart_objects.model.plant_descriptor import PlantDescriptor
from smart_objects.actuators.irrigation_actuator import IrrigationActuator
from smart_objects.device.environment_telemetry import EnvironmentTelemetryData

class TestMqttSensorManager(unittest.TestCase):
    def setUp(self):
        # Usa EnvironmentTelemetryData con sensori reali
        self.env_telemetry = EnvironmentTelemetryData("plant01")
        self.plant_descriptor = PlantDescriptor("cactus", "plant01")
        # Sovrascrivi manualmente la lista dei sensori
        self.plant_descriptor.sensors = [self.env_telemetry.temperature, self.env_telemetry.humidity, self.env_telemetry.lightness, self.env_telemetry.batteryLevel]
        self.manager = MqttSensorManager(self.plant_descriptor)
        self.manager.client.publish = MagicMock()

    def test_publish_telemetry(self):
        self.manager.publish_telemetry()
        # Verifica che publish sia stato chiamato per ogni sensore
        self.assertEqual(self.manager.client.publish.call_count, len(self.plant_descriptor.sensors))
        print("SensorManager publish_telemetry test passed.")

class TestMqttActuatorManager(unittest.TestCase):
    def setUp(self):
        actuator = IrrigationActuator("plant01")
        self.plant_descriptor = PlantDescriptor("cactus", "plant01")
        # Sovrascrivi manualmente la lista degli attuatori
        self.plant_descriptor.actuators = [actuator]
        self.manager = MqttActuatorManager(self.plant_descriptor)
        self.manager.client.publish = MagicMock()

    def test_send_command(self):
        actuator = self.plant_descriptor.actuators[0]
        self.manager.send_command("ON", actuator)
        self.assertTrue(self.manager.client.publish.called)
        print("ActuatorManager send_command test passed.")

if __name__ == "__main__":
    unittest.main()