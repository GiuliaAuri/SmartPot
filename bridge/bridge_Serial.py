import serial
import serial.tools.list_ports
import threading
import configparser
import logging
import time

PLANT_ID = "plant_cactus_001"
SENSOR_TYPE_MAPPING = {
			'H': 'humidity',      # Arduino 'H' -> Python 'humidity'
			'T': 'temperature',   # Arduino 'T' -> Python 'temperature'
			'L': 'lightness',     # Arduino 'L' -> Python 'lightness'
			'W': 'water_flow',    # Arduino 'W' -> Python 'water_flow'
			'B': 'battery_level', # Arduino 'B' -> Python 'battery_level'
			'V': 'level_tank'     # Arduino 'V' -> Python 'level_tank'
		}
        
class Bridge(threading.Thread):
	_instance = None
	_initialized = False

	def __new__(cls):
		if cls._instance is None:
			cls._instance = super(Bridge, cls).__new__(cls)
		return cls._instance

	def __init__(self):
		if not self._initialized:
			super().__init__(daemon=True)
			self.config = configparser.ConfigParser()
			self.config.read('config.ini')
			self.setupSerial()
		self.running = True
		self.lock = threading.Lock()
		self.sensor_values = {}  # Dizionario per multiple tipi di sensori
		self.sensor_timestamps = {}  # Timestamp per ogni sensore
		self.command_queue = []  # Coda per comandi attuatori
		# Mappatura tipi Arduino -> Python
		
		self._initialized = True
		

	def setupSerial(self):
		# open serial port
		self.ser = None
		self.portname = None

		if self.config.getboolean("Serial","UseDescription", fallback=False):
			self.portname = self.config.get("Serial","PortName", fallback="COM1")
			print(f"ARDUINO: Usando porta configurata: {self.portname}")
		else:
			print("ARDUINO: list of available ports: ")
			ports = serial.tools.list_ports.comports()

			for port in ports:
				print ("ARDUINO:"+ port.device)
				print ("ARDUINO:"+ port.description)
				if self.config.get("Serial","PortDescription", fallback="arduino").lower() \
						in port.description.lower():
					self.portname = port.device
					print(f"ARDUINO: Porta trovata per descrizione: {self.portname}")
			
			# Se non trova per descrizione, usa la prima porta disponibile
			if self.portname is None and ports:
				self.portname = ports[0].device
				print(f"ARDUINO: Usando prima porta disponibile: {self.portname}")

		try:
			if self.portname is not None:
				print ("ARDUINO: connecting to " + self.portname)
				self.ser = serial.Serial(self.portname, 9600, timeout=0)
				print("ARDUINO: Connessione seriale stabilita")
			else:
				print("ARDUINO: Nessuna porta seriale disponibile")
		except Exception as e:
			print(f"ARDUINO: Errore connessione seriale: {e}")
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
				print("ARDUINO: Serial port not available!")
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
					print(f"ARDUINO: Byte ricevuto: {lastchar}")

					if lastchar==b'\xfe': #EOL
						print("\nARDUINO: Value received")
						with self.lock:
							self.useData()
							self.inbuffer =[]
					else:
						# append
						self.inbuffer.append (lastchar)
				else:
					# Nessun dato disponibile, aspetta un po'
					time.sleep(0.01)
			else:
				print("ARDUINO: Serial port non disponibile")
				time.sleep(1)
		

	def useData(self):
		# I have received a packet from the serial port. I can use it
		if len(self.inbuffer)<3:   # at least header, size, type, value
			return False
		# split parts
		if self.inbuffer[0] != b'\xff':
			return False

		numval = int.from_bytes(self.inbuffer[1], byteorder='little')
		
		# Arduino invia: FF, numval, tipo1, valore1, tipo2, valore2, ..., FE
		# Per numval=2: buffer[0]=FF, buffer[1]=2, buffer[2]=tipo1, buffer[3]=valore1, buffer[4]=tipo2, buffer[5]=valore2, buffer[6]=FE
		
		# Verifica che abbiamo abbastanza dati: header + numval*2 
		expected_length = 2 + (numval * 2)  # FF + numval + (tipo+valore)*numval 
		if len(self.inbuffer) < expected_length:
			print(f"ARDUINO: Pacchetto incompleto. Attesi {expected_length} bytes, ricevuti {len(self.inbuffer)}")
			return False
		
		current_time = int(time.time())
		
		# Processa ogni coppia tipo-valore
		for i in range(numval):
			type_index = 2 + (i * 2)      # Indice del tipo sensore
			value_index = 2 + (i * 2) + 1  # Indice del valore
			
			if type_index < len(self.inbuffer) and value_index < len(self.inbuffer):
				sensor_type = chr(self.inbuffer[type_index][0])  # Tipo sensore
				val = self.inbuffer[value_index][0]  # Valore diretto (Arduino invia già mappato 0-253)
				
				strval = f"Sensor {i+1}/{numval} {sensor_type}: {val}"
				print("ARDUINO: " + strval)
				
				# Mappa il tipo Arduino al tipo Python e salva il valore
				python_sensor_type = SENSOR_TYPE_MAPPING.get(sensor_type, sensor_type)
				with self.lock:
					self.sensor_values[python_sensor_type] = val
					self.sensor_timestamps[python_sensor_type] = current_time
				print(f"ARDUINO: Mappato {sensor_type} -> {python_sensor_type}: {val} (timestamp: {current_time})")
			else:
				print(f"ARDUINO: Errore nell'accesso ai dati per sensore {i+1}")

	def get_sensor_value(self, sensor_type=None):
		"""
		Ottiene il valore di un sensore specifico.
		Se sensor_type è None, restituisce tutti i valori.
		"""
		with self.lock:
			if sensor_type is None:
				logging.debug(f"Bridge: sensor_type is None")
				return self.sensor_values.copy()
			
			value = self.sensor_values.get(sensor_type, None)
			if value is None:
				logging.debug(f"Bridge: Nessun valore trovato per sensore '{sensor_type}'. Valori disponibili: {list(self.sensor_values.keys())}")
			else:
				logging.debug(f"Bridge: Valore trovato per '{sensor_type}': {value}")
			return value
	
	def get_sensor_timestamp(self, sensor_type):
		"""
		Ottiene il timestamp dell'ultimo aggiornamento di un sensore specifico.
		"""
		with self.lock:
			return self.sensor_timestamps.get(sensor_type, None)
	
	def send_actuator_command(self, actuator_type, command):
		"""
		Invia un comando a un attuatore specifico.
		Arduino si aspetta: tipo_attuatore + comando
		"""
		try:
			if self.ser is not None:
				if actuator_type == "irrigation":
					# Arduino legge: type = Serial.read(); val = Serial.read();
					command_upper = command.upper()
					if command_upper.startswith("ACTIVATE") or command_upper == "ON":
						self.ser.write(b'I')  # Tipo attuatore (ACTUATOR_TYPE)
						self.ser.write(b'A')  # Comando ATTIVA
						print(f"ARDUINO: Comando ATTIVA inviato per {actuator_type}")
					elif command_upper.startswith("DEACTIVATE") or command_upper == "OFF":
						self.ser.write(b'I')  # Tipo attuatore (ACTUATOR_TYPE)
						self.ser.write(b'S')  # Comando DISATTIVA
						print(f"ARDUINO: Comando DISATTIVA inviato per {actuator_type}")
					else:
						print(f"ARDUINO: Comando non riconosciuto per {actuator_type}: {command}")
				else:
					print(f"ARDUINO: Tipo attuatore non supportato: {actuator_type}")
			else:
				print("ARDUINO: Porta seriale non disponibile!")
		except Exception as e:
			logging.error(f"ARDUINO: Errore nell'invio comando attuatore: {e}")
	
	def run(self):
		"""
		Metodo richiesto per threading.Thread.
		Avvia il loop di comunicazione seriale.
		"""
		print("ARDUINO: Bridge seriale avviato")
		self.loop()
	
	def start(self):
		"""
		Avvia il thread del Bridge e restituisce True se la connessione seriale è disponibile.
		"""
		if self.ser is not None:
			super().start()  # Avvia il thread
			return True
		else:
			print("ARDUINO: Porta seriale non disponibile - Bridge non avviato")
			return False
	
	def stop(self):
		self.running = False
		if self.ser is not None:
			self.ser.close()

