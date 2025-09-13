import logging
from plants_system.smart_objects.models.Device import Device
from plants_system.smart_objects.sensors.battery_level_sensor import BatteryLevelSensor
from plants_system.smart_objects.sensors.humidity_sensor import HumiditySensor
from plants_system.smart_objects.sensors.lightness_sensor import LightnessSensor
from plants_system.smart_objects.sensors.temperature_sensor import TemperatureSensor
from plants_system.smart_objects.resources.factory_config import FactoryConfig

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("environment_telemetry")

class EnvironmentTelemetryData(Device):
    def __init__(self, plant_id):
        self.plant_id = plant_id  
        self.device = "environment_telemetry"
        
        # Crea i sensori basandosi sulla configurazione dal PlantFactory
        sensors = self._create_sensors_from_config()
        
        super().__init__(plant_id, self.device, sensors=sensors)
    
    def _create_sensors_from_config(self):
        """Crea i sensori basandosi sulla configurazione"""
        sensors = []
        
        # Valori di default nel caso la configurazione non sia disponibile
        default_configs = {
            'battery_level': {
                'initial_value': 100.0,
                'unit': '%',
                'min_value': 0.0,
                'max_value': 100.0,
                'is_real': False
            },
            'temperature': {
                'initial_value': 25.0,
                'unit': '°C',
                'min_value': -10.0,
                'max_value': 50.0,
                'is_real': False
            },
            'humidity': {
                'initial_value': 50.0,
                'unit': '%',
                'min_value': 0.0,
                'max_value': 100.0,
                'is_real': False
            },
            'lightness': {
                'initial_value': 30000.0,
                'unit': 'lx',
                'min_value': 0.0,
                'max_value': 100000.0,
                'is_real': False
            }
        }
        
        # Crea i sensori basandosi sulla configurazione
        sensor_mapping = {
            'battery_level': BatteryLevelSensor,
            'temperature': TemperatureSensor,
            'humidity': HumiditySensor,
            'lightness': LightnessSensor
        }
        
        for sensor_type, sensor_class in sensor_mapping.items():
            # Ottiene la configurazione dal PlantConfigManager
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

