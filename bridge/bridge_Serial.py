import serial
import serial.tools.list_ports
import threading
import configparser
import logging
import time

PLANT_ID = "plant_cactus_001"

        
class Bridge(threading.Thread):

	def __init__(self):
		super().__init__(daemon=True)
		self.config = configparser.ConfigParser()
		self.config.read('config.ini')
		self.setupSerial()
		self.running = True
		self.lock = threading.Lock()
		self.last_sensor_value = None
		

	def setupSerial(self):
		# open serial port
		self.ser = None

		if self.config.get("Serial","UseDescription", fallback=False):
			self.portname = self.config.get("Serial","PortName", fallback="COM1")
		else:
			print("list of available ports: ")
			ports = serial.tools.list_ports.comports()

			for port in ports:
				print (port.device)
				print (port.description)
				if self.config.get("Serial","PortDescription", fallback="arduino").lower() \
						in port.description.lower():
					self.portname = port.device

		try:
			if self.portname is not None:
				print ("connecting to " + self.portname)
				self.ser = serial.Serial(self.portname, 9600, timeout=0)
		except:
			self.ser = None

		# self.ser.open()

		# internal input buffer from serial
		self.inbuffer = []

	
	

	# TODO update the actuator: type value
	def send_command_switch(self, type:str, command:str):
		try:
			if type == "irrigation":
				self.ser.write(b'I')#TODO byte o solo string?
			if self.ser is not None:
				if command.upper().startswith("ACTIVATE"):
					self.ser.write(b'A')
				elif command.upper().startswith("DEACTIVATE"):
					self.ser.write(b'S')
			else:
				print("Serial port not available!")
		except Exception as e:
			logging.error(f"Error sending command: {e}")

	def loop(self):
		# infinite loop for serial managing
		#
		while self.running:
			#look for a byte from serial
			if not self.ser is None:
				if self.ser.in_waiting>0:
					# data available from the serial port
					lastchar=self.ser.read(1)

					if lastchar==b'\xfe': #EOL
						print("\nValue received")
						with self.lock:
							self.useData()
							self.inbuffer =[]
					else:
						# append
						self.inbuffer.append (lastchar)
		

	def useData(self):
		# I have received a packet from the serial port. I can use it
		if len(self.inbuffer)<3:   # at least header, size, footer
			return False
		# split parts
		if self.inbuffer[0] != b'\xff':
			return False

		numval = int.from_bytes(self.inbuffer[1], byteorder='little')
		type = None
		for i in range (numval):
			if i % 2 == 0:
				type = self.inbuffer[i+2]
			else:
				val = int.from_bytes(self.inbuffer[i+2], byteorder='little')
				strval = "Sensor %d %s: %d " % (i, type, val)
				print(strval)
				self.last_sensor_value = val

	#TODO: update the sensor
	def get_sensor_value(self):
		with self.lock:
			return self.last_sensor_value
	
	def stop(self):
		self.running = False
		if self.ser is not None:
			self.ser.close()

if __name__ == '__main__':
	br=Bridge()
	br.loop()

