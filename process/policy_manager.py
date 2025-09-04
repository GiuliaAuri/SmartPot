import operator
import json
import logging


class PolicyManager:
    OPERATORS = {
        "<": operator.lt,
        ">": operator.gt,
        "=": operator.eq,
        "<=": operator.le,
        ">=": operator.ge
    }

    def __init__(self, policy_path):
        with open(policy_path, "r") as f:
            all_policies = json.load(f)
        self.plant_policies: dict[str, list[dict]] = {p["plant_id"]: p["policies"] for p in all_policies}

    def evaluate(self, plant):
        policies = self.plant_policies.get(plant.plant_id, [])
        for policy in policies:
            sensor = next((s for s in plant.sensors if s.type == policy["sensor"]), None)
            actuator = next((a for a in plant.actuators if a.device == policy["actuator"]), None)
            op = self.OPERATORS.get(policy["condition"])
            if sensor and actuator and op:
                if op(sensor.value, policy["value"]):
                    if policy["action"] == "activate":
                        actuator.status = True
                        logging.info(f"Activated actuator: {actuator.device} - plant: {plant.plant_id}")
                        self.actuator_managers[plant.plant_id].send_command(actuator.device, "ON")
                    elif policy["action"] == "deactivate":
                        actuator.status = False
                        logging.info(f"Deactivated actuator: {actuator.device} - plant: {plant.plant_id}")
                        self.actuator_managers[plant.plant_id].send_command(actuator.device, "OFF")