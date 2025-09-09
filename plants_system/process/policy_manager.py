import operator
import json
import logging
from plants_system.smart_objects.models.plant_descriptor import PlantDescriptor
from plants_system.process.data_collector_producer import DataCollectorProducer


class PolicyManager:
    """
    Gestore delle policy per la valutazione automatica delle condizioni delle piante.
    
    Questa classe gestisce la valutazione delle policy definite per ogni pianta,
    generando alert e azioni basate sui valori dei sensori. Le policy definiscono
    quando attivare/disattivare attuatori o generare alert in base alle condizioni
    ambientali rilevate dai sensori.
    """
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
        """
        Valuta le policy per una pianta specifica.
        
        Questo metodo valuta tutte le policy definite per la pianta specificata,
        generando alert e azioni in base ai valori dei sensori.
        """
        policies = self.plant_policies.get(plant.plant_id, [])
        logging.info(f"Evaluating {len(policies)} policies for plant {plant.plant_id}")
        self.actions[plant.plant_id] = []
        self.alerts[plant.plant_id] = []

        for policy in policies:
            sensor = self._find_sensor(plant, policy["sensor"])
            actuator = self._find_actuator(plant, policy.get("actuator", ""))

            logging.debug(f"Policy: {policy['sensor']} {policy['condition']} {policy['value']} -> {policy['action']}")
            logging.debug(f"Found sensor: {sensor is not None}, Found actuator: {actuator is not None}")
            if sensor:
                logging.debug(f"Sensor value: {sensor.value}")

            op = self.OPERATORS.get(policy["condition"])
            if sensor and op:
                if policy["action"] == "alert":
                    # Per gli alert, non serve l'attuatore
                    alert_msg = policy.get(
                        "message",
                        f"Alert: {sensor.type} value {sensor.value} for plant {plant.plant_id}"
                    )
                    if op(sensor.value, policy["value"]):
                        # Condizione soddisfatta: aggiungi alert se non esiste già
                        if alert_msg not in self.alerts[plant.plant_id]:
                            self.alerts[plant.plant_id].append(alert_msg)
                            logging.info(f"Generated alert for {plant.plant_id}: {alert_msg}")
                    else:
                        # Condizione non più soddisfatta: rimuovi alert se esiste
                        if alert_msg in self.alerts[plant.plant_id]:
                            self.alerts[plant.plant_id].remove(alert_msg)
                            logging.info(f"Resolved alert for {plant.plant_id}: {alert_msg}")
                elif actuator:
                    # Per le azioni, serve l'attuatore
                    if op(sensor.value, policy["value"]):
                        action_str = f"{policy['action'].capitalize()} {actuator.type}"
                        # Evita duplicati
                        if action_str not in self.actions[plant.plant_id]:
                            self.actions[plant.plant_id].append(action_str)

    @staticmethod
    def _find_sensor(plant: PlantDescriptor, sensor_type: str):
        """
        Trova un sensore specifico in una pianta.
        
        Questo metodo cerca un sensore di un tipo specifico nella pianta.
        """
        for device in plant.devices:
            for s in getattr(device, "sensors", []):
                if s.type == sensor_type:
                    return s
        return None

    @staticmethod
    def _find_actuator(plant: PlantDescriptor, actuator_name: str):
        """
        Trova un attuatore specifico in una pianta.
        
        Questo metodo cerca un attuatore con un nome specifico nella pianta.
        """
        for device in plant.devices:
            for a in getattr(device, "actuators", []):
                if a.device == actuator_name:
                    return a
        return None
