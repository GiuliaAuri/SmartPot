# Plants-System

## Smart Home - Vaso Smart per Piante


## Descrizione

L’obiettivo del progetto è la realizzazione di un sistema **IoT** per la gestione intelligente di uno o più vasi per piante, che coinvolga i seguenti dispositivi (sensori e attuatori):

### Dispositivi

| Nome                             | Tipologia         | Descrizione |
|----------------------------------|------------------|-------------|
| **Water Metering Smart Object**  | Sensore, Attuatore | Smart Object associato al monitoraggio e al controllo dei consumi dell’acqua:<br> - Sensore flusso acqua consumata (l/s - liter per second)<br> - Switch Fornitura (ON/OFF) |
| **Tank Monitoring Smart Object** | Sensore           | Smart Object associato al serbatoio di un vaso per il monitoraggio del consumo di acqua:<br> - Sensore di livello |
| **Environmental Monitoring Smart Object** | Sensore | Smart Object dotato dei seguenti sensori per il monitoraggio ambientale:<br> - Sensore di temperatura<br> - Sensore di umidità<br> - Sensore di luminosità<br> - Sensore per il livello di batteria del dispositivo |


## Funzionamento del Sistema

Il progetto sarà progettato per supportare **n dispositivi per ogni tipologia** in funzione delle esigenze delle piante.  
In fase di demo del progetto è possibile emulare il numero minimo di device (fino a 3) per mostrare il corretto funzionamento del sistema sviluppato.
## Architettura

Nell’architettura sarà presente anche un **Data Collector & Manager**, capace di ricevere i dati di tutti i device coinvolti e implementare i seguenti comportamenti:

- Ogni pianta è monitorata da uno o più **Water Metering Smart Object** e **Environmental Monitoring Smart Object**.  
  Ad ogni vaso è associato un serbatoio dotato di **Tank Monitoring**.
- Per ogni vaso sarà possibile definire una **policy di irrigazione configurabile** in base ai dati rilevati (es. umidità del terreno, temperatura e luminosità) e in base alla tipologia di pianta contenuta nel vaso.  
  Se l’umidità scende sotto una soglia predefinita, verrà attivata automaticamente la fornitura d’acqua tramite attuatore.  
  La fornitura sarà disattivata una volta raggiunto un valore ottimale o dopo un tempo massimo impostabile.
- In caso di **batteria bassa** del dispositivo, sarà generato un avviso.
- Quando il **livello di acqua** di un serbatoio scende sotto un determinato livello, verrà generato un avviso all’utente.

## 🌱 Sensori di Telemetria

I sensori monitorano diversi parametri ambientali e di consumo:

- **Temperatura**
- **Umidità**
- **Luminosità**
- **Livello della batteria**
- **Livello del serbatoio**
- **Quantità di acqua consumata**
Tutti questi sensori sono simulati in software.

I dati raccolti vengono **pubblicati** sul topic MQTT con la seguente struttura: 
```
 plant/{plant_id}/device/{device_id}/telemetry/{resource_id}
```
## 💧 Attuatore per l’Irrigazione

L’attuatore che gestisce l’irrigazione non pubblica dati, ma è **sottoscritto** a un topic dedicato ai comandi:
```
plant/{plant_id}/device/{device_id}/command/{resource_id}
```


               +----------------------+
               |   🌱 Pianta          |
               | (Sensori & Attuatori)|
               +----------+-----------+
                          |
                          v
                   +--------------+
                   |  🌀 Broker   |
                   |   MQTT       |
                   +--------------+
                          |
                          v
          +------------------------------+
          |  📡 MQTT Consumer /          |
          |     Data Collector           |
          +--------------+---------------+
                          |
                          v
                   +--------------+
                   |    ☁️ Cloud   |
                   +--------------+

# Parte per l'elaborato
## Componenti principali

- 🌱 **Pianta** (realizzati in hardware)
  - **Sensore di umidità**: rileva il livello di umidità del terreno.  
  - **Attuatore (rele per irrigazione)**: controlla l’erogazione dell’acqua in base ai dati del sensore.  

- ⚡ **Arduino R4 con scheda Wi-Fi**
  - Riceve i dati dai sensori e invia comandi all’attuatore.  
  - Gestisce la comunicazione wireless verso il PC.

- 💻 **PC con Bridge**
  - Funziona come intermediario tra Arduino e il cloud.  
  - Riceve i dati dai dispositivi, li elabora e li inoltra al cloud.  

- ☁️ **Cloud**
  - Memorizza i dati delle piante e dello stato dei dispositivi.  
  - Consente l’accesso remoto tramite applicazioni web.  

- 🌐 **Applicazione Web**
  - Permette all’utente di monitorare le piante, visualizzare i dati in tempo reale e configurare l’irrigazione.


                 +----------------------+
                 |      🌱 Pianta       |
                 | Sensore Umidità      |
                 | Attuatore Rele       |
                 +----------+-----------+
                            |
                            v
                 +----------------------+
                 |   ⚡ Arduino R4       |
                 |  (con scheda Wi-Fi)  |
                 +----------+-----------+
                            |
                            v
                 +----------------------+
                 |      💻 PC           |
                 |   (Bridge installato)|
                 +----------+-----------+
                            |
                            v
                 +----------------------+
                 |       ☁️ Cloud       |
                 +----------+-----------+
                            |
                            v
                 +----------------------+
                 |  🌐 Applicazione Web |
                 +----------------------+

Esempio base di bridge:
```python

### author: Roberto Vezzani

import serial
import serial.tools.list_ports

import configparser

import paho.mqtt.client as mqtt

class Bridge():

	def __init__(self):
		self.config = configparser.ConfigParser()
		self.config.read('config.ini')
		self.setupSerial()
		self.setupMQTT()

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

	def setupMQTT(self):
		self.clientMQTT = mqtt.Client(mqtt.CallbackAPIVersion.VERSION1)
		self.clientMQTT.on_connect = self.on_connect

		print("connecting to MQTT broker...")
		self.clientMQTT.connect(
			self.config.get("MQTT","Server", fallback= "localhost"),
			self.config.getint("MQTT","Port", fallback= 1883),
			60)

		self.clientMQTT.loop_start()

	def on_connect(self, client, userdata, flags, rc):
		print("Connected with result code " + str(rc))


	def loop(self):
		# infinite loop for serial managing
		#
		while (True):
			#look for a byte from serial
			if not self.ser is None:

				if self.ser.in_waiting>0:
					# data available from the serial port
					lastchar=self.ser.read(1)

					if lastchar==b'\xfe': #EOL
						print("\nValue received")
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

		for i in range (numval):
			val = int.from_bytes(self.inbuffer[i+2], byteorder='little')
			strval = "Sensor %d: %d " % (i, val)
			print(strval)
			self.clientMQTT.publish('RVsensor/{:d}'.format(i),'{:d}'.format(val))






if __name__ == '__main__':
	br=Bridge()
	br.loop()

```
