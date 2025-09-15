from typing import ClassVar


class MqttConfigurationParameters(object):
    BROKER_ADDRESS: ClassVar[str] = "127.0.0.1"
    BROKER_PORT: ClassVar[int] = 7883
    MQTT_USERNAME: ClassVar[str] = "<your_username>"
    MQTT_PASSWORD: ClassVar[str] = "<your_password>"
    MQTT_BASIC_TOPIC = "/iot/user/{0}".format(MQTT_USERNAME)
    PLANT_TOPIC = "plant"
    PLANT_TELEMETRY_TOPIC = "telemetry"
    PLANT_INFO_TOPIC = "info"
    BASIC_TOPIC: ClassVar[str] = "plant"
    DEVICE_TOPIC: ClassVar[str] = "device"
    TELEMETRY_TOPIC: ClassVar[str] = "telemetry"
    COMMAND_TOPIC: ClassVar[str] = "command"
    SENSOR_TOPIC: ClassVar[str] = "sensor"
    ACTUATOR_TOPIC: ClassVar[str] = "actuator"
    
    @staticmethod
    def build_telemetry_plant_topic(sensor_id: str) -> str:
        """Build the telemetry topic for a specific plant and sensor, 
        comunication from sensor to cloud.
        e.g., plant/{plant_id}/sensor/{sensor_id}
        plant/plant02/sensor/temperature
        """
        return "{0}/{1}/{2}".format(
            MqttConfigurationParameters.BASIC_TOPIC,
            MqttConfigurationParameters.SENSOR_TOPIC,
            sensor_id
            
        )

    @staticmethod
    def build_command_plant_topic(actuator_id: str) -> str:
        """Build the control topic for a specific plant and device,
        communication from cloud to actuator.
        e.g. plant/actuator/actuator_id
        plant/actuator/irrigation
        """
        return "{0}/{1}/{2}".format(
            MqttConfigurationParameters.BASIC_TOPIC,
            MqttConfigurationParameters.ACTUATOR_TOPIC,
            actuator_id
        )
    
    @staticmethod
    def build_info_plant_topic(plant_id:str) -> str:
        """Build the info topic for a specific plant,
        communication from sensor to cloud.
        e.g., plant/{plant_id}/info
        plant/plant02/info
        """
        return "{0}/{1}/{2}".format(
            MqttConfigurationParameters.BASIC_TOPIC,
            plant_id,
            MqttConfigurationParameters.PLANT_INFO_TOPIC
        )

