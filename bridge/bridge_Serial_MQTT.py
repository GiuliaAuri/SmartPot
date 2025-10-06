import serial
import serial.tools.list_ports
import configparser
import sys
import os
import time

# Aggiungi il path per importare i moduli del progetto
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from conf.mqtt_conf_params import MqttConfigurationParameters
import paho.mqtt.client as mqtt
SENSOR_MAPPING = {
        'H': "humidity",
        'T': "temperature", 
        'L': "lightness",
        'B': "battery_level"
    }
ACTUATOR_MAPPING = {
    0: "irrigation",  # ID → Nome
}

ACTUATOR_CHAR_MAPPING = {
    0: b'I',  # irrigation
    
}

class Bridge():

	def __init__(self):
		self.config = configparser.ConfigParser()
		self.config.read('config.ini')
		self.setupSerial()
		self.setupMQTT()

	def setupSerial(self):
		# open serial port
		self.ser = None
		self.portname = None

		if self.config.get("Serial","UseDescription", fallback=False):
			self.portname = self.config.get("Serial","PortName", fallback="COM5")
		else:
			print("list of available ports: ")
			ports = serial.tools.list_ports.comports()

			for port in ports:
				print (port.device)
				print (port.description)
				if self.config.get("Serial","PortDescription", fallback="arduino").lower() \
						in port.description.lower():
					self.portname = port.device
			
			# Se non trova la porta per descrizione, usa PortName
			if self.portname is None:
				self.portname = self.config.get("Serial","PortName", fallback="COM5")
				print(f"Usando porta configurata: {self.portname}")

		try:
			if self.portname is not None:
				print ("connecting to " + self.portname)
				self.ser = serial.Serial(self.portname, 9600, timeout=0)
				print(f"✅ Connesso alla porta {self.portname}")
			else:
				print("❌ Nessuna porta trovata")
		except Exception as e:
			print(f"❌ Errore connessione seriale: {e}")
			self.ser = None

		# self.ser.open()

		# internal input buffer from serial
		self.inbuffer = []

	def setupMQTT(self):
		self.clientMQTT = mqtt.Client()
		self.clientMQTT.on_connect = self.on_connect
		self.clientMQTT.on_message = self.on_message
		print("connecting to MQTT broker...")
		self.clientMQTT.connect(
			self.config.get("MQTT","Server", fallback= "localhost"),
			self.config.getint("MQTT","Port", fallback= 7883),
			60)

		self.clientMQTT.loop_start()

	def on_connect(self, client, userdata, flags, rc):
		print("Connected with result code " + str(rc))
		
		for actuator_id, actuator_name in ACTUATOR_MAPPING.items():
			topic = MqttConfigurationParameters.build_command_plant_topic(actuator_name)
			self.clientMQTT.subscribe(topic)
			print(f"✅ Sottoscritto a: {topic}")
			
	def on_message(self, client, userdata, msg):
		print(f"Comando ricevuto - Topic: {msg.topic}, Payload: {msg.payload}")
		
		topic_parts = msg.topic.split('/')
		actuator_type = topic_parts[-1]  # "irrigation", "lighting", etc.
		
		actuator_id = None
		for id, name in ACTUATOR_MAPPING.items():
			if name == actuator_type:
				actuator_id = id
				break
		
		if actuator_id is None:
			print(f"Attuatore non riconosciuto: {actuator_type}")
			return
		
		actuator_char = ACTUATOR_CHAR_MAPPING.get(actuator_id)
		if not actuator_char:
			print(f"Carattere seriale non trovato per attuatore {actuator_id}")
			return
		
		command = msg.payload.decode('utf-8').lower()
		
		if self.ser is not None:
			if command == "start" or command == "on" or command == "1":
				self.ser.write(actuator_char)  # Tipo attuatore
				self.ser.write(b'A')  # Comando ATTIVA
				print(f"Comando ATTIVA inviato per {actuator_type}")
			elif command == "stop" or command == "off" or command == "0":
				self.ser.write(actuator_char)  # Tipo attuatore
				self.ser.write(b'S')  # Comando DISATTIVA
				print(f"Comando DISATTIVA inviato per {actuator_type}")
			else:
				print(f"Comando non riconosciuto: {command}")
		else:
			print("Serial port not available!")
			
	def loop(self):
		while (True):
			if not self.ser is None:
				if self.ser.in_waiting>0:
					lastchar=self.ser.read(1)
					print(f"📨 Byte ricevuto da Arduino: {lastchar.hex()}")

					if lastchar==b'\xfe': #EOL
						print("\n✅ Pacchetto completo ricevuto da Arduino")
						self.useData()
						self.inbuffer =[]
					else:
						
						self.inbuffer.append (lastchar)
			else:
				if self.ser is None:
					print("⚠️ Arduino non connesso - nessun dato in arrivo")
					time.sleep(5)  

	def useData(self):
		if len(self.inbuffer)<3:   # at least header, size, footer
			return False
		# split parts
		if self.inbuffer[0] != b'\xff':
			return False

		numval = int.from_bytes(self.inbuffer[1], byteorder='little')

		# Message structure: FF + num_sensori + (tipo_sensore + valore) * numval + FE
		for i in range(numval):
			sensor_offset = 2 + i * 2
			
			if len(self.inbuffer) >= sensor_offset + 2:  
				sensor_type_char = self.inbuffer[sensor_offset].decode('utf-8')
				sensor_value = int.from_bytes(self.inbuffer[sensor_offset + 1], byteorder='little')
				
				sensor_name = SENSOR_MAPPING.get(sensor_type_char, f"sensor_{sensor_type_char}")
				strval = "Sensor %s (%s): %d " % (sensor_name, sensor_type_char, sensor_value)
				print(strval)
                
				topic = MqttConfigurationParameters.build_telemetry_plant_topic(sensor_name)
				payload = '{:d}'.format(sensor_value)
				print(f"📤 MQTT publish - Topic: {topic}, Payload: {payload}")
				self.clientMQTT.publish(topic, payload)

if __name__ == '__main__':
	try:
		print("🌉 Starting Serial-MQTT Bridge...")
		print("📡 Arduino -> MQTT connection")
		print("🔧 Press Ctrl+C to stop")
		print("=" * 50)
        
		br = Bridge()
		br.loop()
        
	except KeyboardInterrupt:
		print("\n🛑 Keyboard interrupt (Ctrl+C)")
		print("🔄 Closing connections...")
        
		# Close serial connection
		if hasattr(br, 'ser') and br.ser is not None:
			br.ser.close()
			print("✅ Serial connection closed")
        
		# Close MQTT connection
		if hasattr(br, 'clientMQTT'):
			br.clientMQTT.loop_stop()
			br.clientMQTT.disconnect()
			print("✅ MQTT connection closed")
        
		print("✅ Bridge terminated successfully")
		
	