import json
from plants_system.smart_objects.models.plant_descriptor import PlantDescriptor
from plants_system.smart_objects.sensors.temperature_sensor import TemperatureSensor
from plants_system.smart_objects.sensors.humidity_sensor import HumiditySensor
from plants_system.smart_objects.devices.tank_monitoring import TankMonitoring
from plants_system.smart_objects.devices.water_metering import WaterMetering
from plants_system.smart_objects.devices.environment_telemetry import EnvironmentTelemetryData
from plants_system.smart_objects.models.SwitchActuator import SwitchActuator

class PlantFactory:
    """
    Factory per la creazione di piante da file JSON.
    
    Questa classe permette di creare oggetti PlantDescriptor da file JSON,
    contenenti informazioni base sulla pianta come nome e tipo.
    """
    @staticmethod
    def create_plants_from_json(json_path):
        with open(json_path, "r") as f:
            config_data = json.load(f)
        
        plants = []
        for plant_config in config_data.get("plants", []):
            plant = PlantFactory._create_plant_from_config(plant_config)
            plants.append(plant)
        
        return plants

    @staticmethod
    def _create_plant_from_config(plant_config):
        plant_id = plant_config["plant_id"]
        species = plant_config["species"]

        # Check if it's the complex format (with devices) or simple (with sensors/actuators)
        if "devices" in plant_config:
            # Complex format: {"devices": {...}}
            devices = []
            for device_name, device_config in plant_config.get("devices", {}).items():
                if device_config.get("enabled", True):
                    device = PlantFactory._create_device_from_config(plant_id, device_name, device_config)
                    devices.append(device)
        else:
            # Simple format: {"sensors": [...], "actuators": [...]}
            devices = PlantFactory._create_default_devices_from_simple_config(plant_id, plant_config)

        return PlantDescriptor(
            species=species,
            plant_id=plant_id,
            devices=devices
        )

    @staticmethod
    def _create_device_from_config(plant_id, device_name, device_config):
        if device_name == "environment_telemetry":
            device = EnvironmentTelemetryData(plant_id)
            # Configure sensors based on config
            if "sensors" in device_config:
                device.sensors = []
                for sensor_type, sensor_config in device_config["sensors"].items():
                    if sensor_config.get("enabled", True):
                        sensor = PlantFactory._create_sensor(plant_id, sensor_type, sensor_config, device_name)
                        device.sensors.append(sensor)
            # Configure actuators if any
            if "actuators" in device_config:
                device.actuators = []
                for actuator_type, actuator_config in device_config["actuators"].items():
                    if actuator_config.get("enabled", True):
                        actuator = PlantFactory._create_actuator(plant_id, actuator_type, actuator_config, device_name)
                        device.actuators.append(actuator)
            return device
        elif device_name == "tank_monitoring":
            device = TankMonitoring(plant_id)
            if "sensors" in device_config:
                device.sensors = []
                for sensor_type, sensor_config in device_config["sensors"].items():
                    if sensor_config.get("enabled", True):
                        sensor = PlantFactory._create_sensor(plant_id, sensor_type, sensor_config, device_name)
                        device.sensors.append(sensor)
            return device
        elif device_name == "water_metering":
            device = WaterMetering(plant_id)
            if "sensors" in device_config:
                device.sensors = []
                for sensor_type, sensor_config in device_config["sensors"].items():
                    if sensor_config.get("enabled", True):
                        sensor = PlantFactory._create_sensor(plant_id, sensor_type, sensor_config, device_name)
                        device.sensors.append(sensor)
            if "actuators" in device_config:
                device.actuators = []
                for actuator_type, actuator_config in device_config["actuators"].items():
                    if actuator_config.get("enabled", True):
                        actuator = PlantFactory._create_actuator(plant_id, actuator_type, actuator_config, device_name)
                        device.actuators.append(actuator)
            return device
        else:
            raise ValueError(f"Unknown device type: {device_name}")

    @staticmethod
    def _create_sensor(plant_id, sensor_type, sensor_config, device_name):
        is_real = sensor_config.get("is_real", False)
        
        if sensor_type == "temperature":
            from plants_system.smart_objects.sensors.temperature_sensor import TemperatureSensor
            return TemperatureSensor(
                plant_id=plant_id,
                initial_value=sensor_config["initial_value"],
                unit=sensor_config["unit"],
                min_value=sensor_config["min_value"],
                max_value=sensor_config["max_value"],
                device=device_name,
                is_real=is_real
            )
        elif sensor_type == "humidity":
            from plants_system.smart_objects.sensors.humidity_sensor import HumiditySensor
            return HumiditySensor(
                plant_id=plant_id,
                initial_value=sensor_config["initial_value"],
                unit=sensor_config["unit"],
                min_value=sensor_config["min_value"],
                max_value=sensor_config["max_value"],
                device=device_name,
                is_real=is_real
            )
        elif sensor_type == "lightness":
            from plants_system.smart_objects.sensors.lightness_sensor import LightnessSensor
            return LightnessSensor(
                plant_id=plant_id,
                initial_value=sensor_config["initial_value"],
                unit=sensor_config["unit"],
                min_value=sensor_config["min_value"],
                max_value=sensor_config["max_value"],
                device=device_name,
                is_real=is_real
            )
        elif sensor_type == "battery_level":
            from plants_system.smart_objects.sensors.battery_level_sensor import BatteryLevelSensor
            return BatteryLevelSensor(
                plant_id=plant_id,
                initial_value=sensor_config["initial_value"],
                unit=sensor_config["unit"],
                min_value=sensor_config["min_value"],
                max_value=sensor_config["max_value"],
                device=device_name,
                is_real=is_real
            )
        elif sensor_type == "level_tank":
            from plants_system.smart_objects.sensors.level_tank_sensor import LevelTankSensor
            return LevelTankSensor(
                plant_id=plant_id,
                initial_value=sensor_config["initial_value"],
                unit=sensor_config["unit"],
                min_value=sensor_config["min_value"],
                max_value=sensor_config["max_value"],
                device=device_name,
                is_real=is_real
            )
        elif sensor_type == "water_flow":
            from plants_system.smart_objects.sensors.water_flow_sensor import WaterFlowSensor
            return WaterFlowSensor(
                plant_id=plant_id,
                initial_value=sensor_config["initial_value"],
                unit=sensor_config["unit"],
                min_value=sensor_config["min_value"],
                max_value=sensor_config["max_value"],
                device=device_name,
                is_real=is_real
            )
        else:
            raise ValueError(f"Unknown sensor type: {sensor_type}")

    @staticmethod
    def _create_actuator(plant_id, actuator_type, actuator_config, device_name):
        is_real = actuator_config.get("is_real", False)
        
        if actuator_type == "irrigation":
            from plants_system.smart_objects.actuators.irrigation_actuator import IrrigationActuator
            return IrrigationActuator(
                plant_id=plant_id,
                device=device_name,
                is_real=is_real
            )
        else:
            raise ValueError(f"Unknown actuator type: {actuator_type}")

    @staticmethod
    def _create_default_devices_from_simple_config(plant_id, plant_config):
        """
        Crea dispositivi di default dal formato semplice (sensors/actuators lists).
        """
        from plants_system.smart_objects.devices.environment_telemetry import EnvironmentTelemetryData
        from plants_system.smart_objects.devices.tank_monitoring import TankMonitoring
        from plants_system.smart_objects.devices.water_metering import WaterMetering

        devices = []

        env_device = EnvironmentTelemetryData(plant_id)
        specified_sensors = plant_config.get("sensors", [])

        env_device.sensors = [sensor for sensor in env_device.sensors
                             if sensor.type in specified_sensors]
        devices.append(env_device)

        if "level_tank" in specified_sensors:
            tank_device = TankMonitoring(plant_id)
            devices.append(tank_device)

        if "water_flow" in specified_sensors or "irrigation" in plant_config.get("actuators", []):
            water_device = WaterMetering(plant_id)
            if "water_flow" in specified_sensors:
                water_device.sensors = [sensor for sensor in water_device.sensors
                                      if sensor.type == "water_flow"]
            else:
                water_device.sensors = []

            if "irrigation" in plant_config.get("actuators", []):
                water_device.actuators = [actuator for actuator in water_device.actuators
                                        if actuator.type == "irrigation"]
            else:
                water_device.actuators = []

            devices.append(water_device)

        return devices