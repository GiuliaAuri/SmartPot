import operator
import json
import logging
from plants_system.smart_objects.models.plant_descriptor import PlantDescriptor
from plants_system.process.data_collector_producer import DataCollectorProducer


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
        self.plant_policies: dict[str, list[dict]] = {
            p["plant_id"]: p["policies"] for p in all_policies
        }
        self.actions: dict[str, list[str]] = {}  # plant_id -> list of actions
        self.alerts: dict[str, list[str]] = {}   # plant_id -> list of alerts

    def evaluate(self, plant: PlantDescriptor):
        policies = self.plant_policies.get(plant.plant_id, [])
        self.actions[plant.plant_id] = []
        self.alerts[plant.plant_id] = []

        logged_sensors = set()  # evita duplicati nei log

        for policy in policies:
            sensor = self._find_sensor(plant, policy["sensor"])
            actuator = self._find_actuator(plant, policy.get("actuator", ""))

            # loggalo solo la prima volta che lo vedi
            if sensor and policy["sensor"] not in logged_sensors:
                #print(f"DEBUG: plant={plant.plant_id}, sensor={sensor.type}, value={sensor.value}")
                logged_sensors.add(policy["sensor"])

            op = self.OPERATORS.get(policy["condition"])
            if sensor and op:
                
                if op(sensor.value, policy["value"]):
                    if policy["action"] == "activate" and actuator:
                        self.actions[plant.plant_id].append(f"Activate {actuator.device}")
                    elif policy["action"] == "deactivate" and actuator:
                        self.actions[plant.plant_id].append(f"Deactivate {actuator.device}")
                    elif policy["action"] == "alert":
                        alert_msg = policy.get(
                            "message",
                            f"Alert: {sensor.type} value {sensor.value} for plant {plant.plant_id}"
                        )
                        self.alerts[plant.plant_id].append(alert_msg)

                #if command is not None:
                    # pubblica comando MQTT
                 #   data_collector_producer = DataCollectorProducer(plant, command)
                  #  data_collector_producer.run()

    @staticmethod
    def _find_sensor(plant: PlantDescriptor, sensor_type: str):
        for device in plant.devices:
            for s in getattr(device, "sensors", []):
                if s.type == sensor_type:
                    return s
        return None

    @staticmethod
    def _find_actuator(plant: PlantDescriptor, actuator_name: str):
        for device in plant.devices:
            for a in getattr(device, "actuators", []):
                if a.device == actuator_name:
                    return a
        return None
