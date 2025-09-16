#!/usr/bin/env python3
"""
PolicyManager Semplificato - Gestione delle policy per il sistema data collector.

Questo PolicyManager:
- Legge le policy dal file JSON
- Valuta le condizioni sui valori dei sensori
- Genera azioni per gli attuatori
- Genera alert quando necessario
"""  

import json
import os
import sys
import logging
from typing import Dict, List, Tuple, Optional

# Aggiungi il path per importare i moduli del progetto
project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
sys.path.insert(0, project_root)

from data_collector.plant_descriptor import PlantDescriptor
from data_collector.data_collector_producer import DataCollectorProducer

class PolicyManager:
    """
    Gestore semplificato delle policy per la valutazione automatica delle condizioni.
    
    Legge le policy dal file policies_conf.json e valuta le condizioni sui valori
    dei sensori per generare azioni e alert.
    """
    
    OPERATORS = {
        "<": lambda x, y: x < y,
        ">": lambda x, y: x > y,
        "=": lambda x, y: x == y,
        "<=": lambda x, y: x <= y,
        ">=": lambda x, y: x >= y
    }
    
    def __init__(self, policy_file_path: str = "data_collector/policies/policies_conf.json"):
        """
        Inizializza il PolicyManager.
        
        Args:
            policy_file_path: Percorso del file delle policy
        """
        self.policy_file_path = policy_file_path
        self.policies = self._load_policies()
        # Stato degli attuatori per ogni pianta {plant_id: {actuator_type: state}}
        self.actuator_states = {}
        logging.info(f"PolicyManager inizializzato con {len(self.policies)} piante")
    
    def _load_policies(self) -> Dict[str, List[Dict]]:
        """
        Carica le policy dal file JSON.
        
        Returns:
            Dizionario con plant_id -> lista di policy
        """
        try:
            if not os.path.exists(self.policy_file_path):
                logging.warning(f"File policy non trovato: {self.policy_file_path}")
                return {}
            
            with open(self.policy_file_path, 'r', encoding='utf-8') as f:
                data = json.load(f)
            
            # Converte la struttura in dizionario
            policies_dict = {}
            for plant_policy in data:
                plant_id = plant_policy.get("plant_id")
                policies = plant_policy.get("policies", [])
                if plant_id:
                    policies_dict[plant_id] = policies
                    logging.info(f"Caricate {len(policies)} policy per {plant_id}")
            
            return policies_dict
            
        except Exception as e:
            logging.error(f"Errore caricamento policy: {e}")
            return {}
    
    def evaluate_policies(self, plant: PlantDescriptor, sensor_values: Dict[str, float]) -> Tuple[List[str], List[str]]:
        """
        Valuta le policy per una pianta con i valori dei sensori.
        
        Args:
            plant: PlantDescriptor della pianta
            sensor_values: Dizionario con i valori dei sensori {sensor_type: value}
            
        Returns:
            Tuple (actions, alerts) - Lista di azioni e alert generati
        """
        plant_id = plant.plant_id
        policies = self.policies.get(plant_id, [])
        
        if not policies:
            logging.debug(f"Nessuna policy trovata per {plant_id}")
            return [], []
        
        # Inizializza lo stato degli attuatori per questa pianta se non esiste
        if plant_id not in self.actuator_states:
            self.actuator_states[plant_id] = {}
        
        actions = []
        alerts = []
        
        logging.info(f"Valutazione {len(policies)} policy per {plant_id}")
        
        for policy in policies:
            try:
                sensor_type = policy.get("sensor")
                condition = policy.get("condition")
                threshold_value = policy.get("value")
                action = policy.get("action")
                
                if not all([sensor_type, condition, threshold_value, action]):
                    logging.warning(f"Policy incompleta per {plant_id}: {policy}")
                    continue
                
                # Verifica se abbiamo il valore del sensore
                if sensor_type not in sensor_values:
                    logging.debug(f"Sensore {sensor_type} non disponibile per {plant_id}")
                    continue
                
                sensor_value = sensor_values[sensor_type]
                
                # Verifica se l'operatore è valido
                if condition not in self.OPERATORS:
                    logging.warning(f"Operatore non valido: {condition}")
                    continue
                
                # Valuta la condizione
                operator_func = self.OPERATORS[condition]
                condition_met = operator_func(sensor_value, threshold_value)
                
                logging.debug(f"Policy {plant_id}: {sensor_type} {condition} {threshold_value} -> {sensor_value} = {condition_met}")
                
                if condition_met:
                    if action == "alert":
                        # Genera alert
                        message = policy.get("message", f"Alert: {sensor_type} {condition} {threshold_value}")
                        alerts.append(message)
                        logging.info(f"Alert generato per {plant_id}: {message}")
                    
                    elif action in ["activate", "start", "on"]:
                        # Attiva attuatore solo se non è già attivo
                        actuator_type = policy.get("actuator", "irrigation")
                        current_state = self.actuator_states[plant_id].get(actuator_type, "off")
                        
                        if current_state != "on":
                            action_str = f"Activate {actuator_type}"
                            actions.append(action_str)
                            self.actuator_states[plant_id][actuator_type] = "on"
                            logging.info(f"Azione generata per {plant_id}: {action_str}")
                        else:
                            logging.debug(f"Attuatore {actuator_type} già attivo per {plant_id}")
                    
                    elif action in ["deactivate", "stop", "off"]:
                        # Disattiva attuatore solo se è attivo
                        actuator_type = policy.get("actuator", "irrigation")
                        current_state = self.actuator_states[plant_id].get(actuator_type, "off")
                        
                        if current_state != "off":
                            action_str = f"Deactivate {actuator_type}"
                            actions.append(action_str)
                            self.actuator_states[plant_id][actuator_type] = "off"
                            logging.info(f"Azione generata per {plant_id}: {action_str}")
                        else:
                            logging.debug(f"Attuatore {actuator_type} già disattivo per {plant_id}")
                    
                    else:
                        logging.warning(f"Azione non riconosciuta: {action}")
                
            except Exception as e:
                logging.error(f"Errore valutazione policy per {plant_id}: {e}")
                continue
        
        return actions, alerts
    
    def execute_actions(self, plant: PlantDescriptor, actions: List[str]) -> None:
        """
        Esegue le azioni generate dalle policy.
        
        Args:
            plant: PlantDescriptor della pianta
            actions: Lista di azioni da eseguire
        """
        if not actions:
            return
        
        for action in actions:
            try:
                logging.info(f"Esecuzione azione per {plant.plant_id}: {action}")
                
                # Crea producer per eseguire l'azione
                producer = DataCollectorProducer(plant, action)
                producer.run()
                
                logging.info(f"Azione eseguita: {action}")
                
            except Exception as e:
                logging.error(f"Errore esecuzione azione {action} per {plant.plant_id}: {e}")
    
    def get_policies_for_plant(self, plant_id: str) -> List[Dict]:
        """
        Restituisce le policy per una pianta specifica.
        
        Args:
            plant_id: ID della pianta
            
        Returns:
            Lista delle policy per la pianta
        """
        return self.policies.get(plant_id, [])
    
    def reload_policies(self) -> None:
        """Ricarica le policy dal file."""
        self.policies = self._load_policies()
        logging.info("Policy ricaricate")

# Test del PolicyManager
if __name__ == "__main__":
    # Configura logging
    logging.basicConfig(level=logging.INFO)
    
    # Test del PolicyManager
    manager = PolicyManager()
    
    # Crea plant descriptor di test
    from data_collector.factory.factory import Factory
    plants = Factory.create_plant_descriptor()
    if plants:
        plant = plants[0]
        
        # Simula valori sensori
        sensor_values = {
            "humidity": 150,  # Sotto la soglia di 200 -> dovrebbe attivare irrigazione
            "battery_level": 15,  # Sotto la soglia di 20 -> dovrebbe generare alert
            "level_tank": 0.2  # Sotto la soglia di 0.3 -> dovrebbe generare alert
        }
        
        print(f"🧪 Test PolicyManager per {plant.plant_id}")
        print(f"📊 Valori sensori: {sensor_values}")
        
        # Valuta policy
        actions, alerts = manager.evaluate_policies(plant, sensor_values)
        
        print(f"📤 Azioni generate: {actions}")
        print(f"🚨 Alert generati: {alerts}")
        
        # Esegui azioni
        if actions:
            print(f"⚡ Esecuzione azioni...")
            manager.execute_actions(plant, actions)
        
        print("✅ Test completato")
