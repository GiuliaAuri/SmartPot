import aiocoap.resource as resource
import aiocoap
import aiocoap.numbers as numbers
import time
from model.SwitchActuator import SwitchActuator
from aiocoap.numbers.codes import Code
from kpn_senml import *
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("irrigation-actuator")
#TODO fare una versione MQTT di questa classe

class IrrigationActuatorResource(resource.Resource):
    """Example Temperature Sensor resources which supports only the GET Method and the Json Format."""

    def __init__(self, device_name):
        super().__init__()
        self.device_name = device_name
        self.if_ = "core.a"
        self.ct = numbers.media_types_rev['application/senml+json']
        self.rt = "it.unimore.device.irrigation"
        self.title = "Irrigation Actuator"
        self.actuator = SwitchActuator()

    def build_senml_json_payload(self):
        pack = SenmlPack(self.device_name)
        temp = SenmlRecord("irrigation-switch",
                           value=self.actuator.status,
                           time=int(time.time()))
        pack.add(temp)
        return pack.to_json()

    async def render_get(self, request):
        logging.info("GET Request Received ...")
        logging.info("Reading updated irrigation actuator value ...")
        logging.info("Updated irrigation actuator value: %s", self.actuator.status)

        payload_string = self.build_senml_json_payload()

        return aiocoap.Message(content_format=numbers.media_types_rev['application/senml+json'],
                               payload=payload_string.encode('utf8'))

    async def render_post(self, request):
        self.actuator.change_status()
        logging.info("Status changed to: %s" % self.actuator.status)
        return aiocoap.Message(code=Code.CHANGED)

    async def render_put(self, request):
        old_status = self.actuator.status
        payload_string = request.payload.decode('UTF-8')
        if payload_string == "false":
            self.actuator.status = False
        elif payload_string == "true":
            self.actuator.status = True
        else:
            return aiocoap.Message(code=Code.BAD_REQUEST)

        if old_status != self.actuator.status:
            logging.info("Status changed to: %s" % self.actuator.status)

        return aiocoap.Message(code=Code.CHANGED)
