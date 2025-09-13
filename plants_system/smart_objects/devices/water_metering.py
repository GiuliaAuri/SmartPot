
import logging
from plants_system.smart_objects.actuators.irrigation_actuator import IrrigationActuator
from plants_system.smart_objects.models.Device import Device
from plants_system.smart_objects.sensors.water_flow_sensor import WaterFlowSensor
from plants_system.smart_objects.resources.factory_config import FactoryConfig

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("water_metering")

class WaterMetering(Device):

    def __init__(self, plant_id: str):
        self.plant_id = plant_id
        self.device = "water_metering"
        
        # Crea i sensori e attuatori basandosi sulla configurazione dal PlantFactory
        sensors = self._create_sensors_from_config()
        actuators = self._create_actuators_from_config()
        
        super().__init__(plant_id, self.device, sensors=sensors, actuators=actuators)
    
    def _create_sensors_from_config(self):
        """Crea i sensori basandosi sulla configurazione"""
        sensors = []
        
        # Valori di default nel caso la configurazione non sia disponibile
        default_configs = {
            'water_flow': {
                'initial_value': 2.0,
                'unit': 'l/s',
                'min_value': 0.0,
                'max_value': 5.0,
                'is_real': False
            }
        }
        
        # Crea i sensori basandosi sulla configurazione
        sensor_mapping = {
            'water_flow': WaterFlowSensor
        }
        
        for sensor_type, sensor_class in sensor_mapping.items():
            # Ottiene la configurazione dal FactoryConfig
            config = FactoryConfig.get_sensor_config(self.plant_id, self.device, sensor_type)
            
            # Se non c'è configurazione, usa i valori di default
            if not config:
                config = default_configs[sensor_type]
            
            # Verifica se il sensore è abilitato
            if config.get('enabled', True):
                try:
                    sensor = sensor_class(
                        plant_id=self.plant_id,
                        initial_value=config.get('initial_value', default_configs[sensor_type]['initial_value']),
                        unit=config.get('unit', default_configs[sensor_type]['unit']),
                        min_value=config.get('min_value', default_configs[sensor_type]['min_value']),
                        max_value=config.get('max_value', default_configs[sensor_type]['max_value']),
                        device=self.device,
                        is_real=config.get('is_real', default_configs[sensor_type]['is_real'])
                    )
                    sensors.append(sensor)
                    logger.info(f"Sensore {sensor_type} creato per {self.plant_id} con valore iniziale {config.get('initial_value')}")
                except Exception as e:
                    logger.error(f"Errore nella creazione del sensore {sensor_type}: {e}")
        
        return sensors
    
    def _create_actuators_from_config(self):
        """Crea gli attuatori basandosi sulla configurazione"""
        actuators = []
        
        # Valori di default nel caso la configurazione non sia disponibile
        default_configs = {
            'irrigation': {
                'is_real': False
            }
        }
        
        # Crea gli attuatori basandosi sulla configurazione
        actuator_mapping = {
            'irrigation': IrrigationActuator
        }
        
        for actuator_type, actuator_class in actuator_mapping.items():
            # Ottiene la configurazione dal FactoryConfig
            config = FactoryConfig.get_actuator_config(self.plant_id, self.device, actuator_type)
            
            # Se non c'è configurazione, usa i valori di default
            if not config:
                config = default_configs[actuator_type]
            
            # Verifica se l'attuatore è abilitato
            if config.get('enabled', True):
                try:
                    actuator = actuator_class(
                        plant_id=self.plant_id,
                        device=self.device,
                        is_real=config.get('is_real', default_configs[actuator_type]['is_real'])
                    )
                    actuators.append(actuator)
                    logger.info(f"Attuatore {actuator_type} creato per {self.plant_id}")
                except Exception as e:
                    logger.error(f"Errore nella creazione dell'attuatore {actuator_type}: {e}")
        
        return actuators
        