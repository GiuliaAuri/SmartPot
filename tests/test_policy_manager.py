import sys
import os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
import unittest
from unittest.mock import MagicMock
from process.policy_manager import PolicyManager
from smart_objects.model.plant_descriptor import PlantDescriptor

class TestPolicyManager(unittest.TestCase):
    def setUp(self):
        # Crea un file di policy temporaneo
        self.test_policy_json = "test_policies_conf.json"
        policies_data = [
            {
                "plant_id": "plant_cactus_001",
                "policies": [
                    {
                        "sensor": "humidity",
                        "actuator": "irrigation_actuator",
                        "condition": "<",
                        "value": 30,
                        "action": "activate"
                    }
                ]
            }
        ]
        with open(self.test_policy_json, "w") as f:
            import json
            json.dump(policies_data, f)
        self.manager = PolicyManager(self.test_policy_json)
        # Mock actuator manager
        self.manager.actuator_managers = {"plant_cactus_001": MagicMock()}
        # Crea una pianta di test con sensore e attuatore mock
        self.plant = PlantDescriptor(species="cactus", plant_id="plant_cactus_001")
        humidity_sensor = MagicMock()
        humidity_sensor.type = "humidity"
        humidity_sensor.value = 20
        irrigation_actuator = MagicMock()
        irrigation_actuator.device = "irrigation_actuator"
        self.plant.sensors = [humidity_sensor]
        self.plant.actuators = [irrigation_actuator]

    def tearDown(self):
        import os
        if os.path.exists(self.test_policy_json):
            os.remove(self.test_policy_json)

    def test_evaluate_activate(self):
        self.manager.evaluate(self.plant)
        self.manager.actuator_managers["plant_cactus_001"].send_command.assert_called_with("irrigation_actuator", "ON")

    def test_evaluate_deactivate(self):
        # Modifica la policy per testare la disattivazione
        self.manager.plant_policies["plant_cactus_001"][0]["action"] = "deactivate"
        self.manager.evaluate(self.plant)
        self.manager.actuator_managers["plant_cactus_001"].send_command.assert_called_with("irrigation_actuator", "OFF")

if __name__ == "__main__":
    unittest.main()