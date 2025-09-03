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

    #TODO DA AGGIUSTARE LA COERENZA

    @staticmethod
    def build_telemetry_plant_topic(
        plant_id: str, device_id: str, resource_id: str
    ) -> str:
        """Build the telemetry topic for a specific plant and device, 
        comunication from sensor to cloud.
        e.g., plant/{plant_id}/device/{device_id}/telemetry/{resource_id}
        plant/plant02/device/environmental_monitoring/telemetry/temperature
        """
        return "{0}/{1}/{2}/{3}/{4}/{5}".format(
            MqttConfigurationParameters.BASIC_TOPIC,
            plant_id,
            MqttConfigurationParameters.DEVICE_TOPIC,
            device_id,
            MqttConfigurationParameters.TELEMETRY_TOPIC,
            resource_id,
        )

    @staticmethod
    def build_command_plant_topic(plant_id: str, device_id: str) -> str:
        """Build the control topic for a specific plant and device,
        communication from cloud to actuator.
        e.g. plant/{plant_id}/device/{device_id}/command
        """
        return "{0}/{1}/{2}/{3}/{4}".format(
            MqttConfigurationParameters.BASIC_TOPIC,
            plant_id,
            MqttConfigurationParameters.DEVICE_TOPIC,
            device_id,
            MqttConfigurationParameters.COMMAND_TOPIC
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

