# 🌱 Smartpot: prototipo di vaso intelligente per la cura automatizzata delle piante

**Smart Pot** è un sistema IoT *end-to-end* progettato per l'automazione, il monitoraggio e la cura a distanza delle piante d'appartamento. L'obiettivo principale è prevenire gli errori di irrigazione consentendo sia un'erogazione automatica dell'acqua basata su soglie configurabili, sia un controllo manuale remoto tramite web app.

Il sistema raccoglie i dati dal sensore di umidità del terreno tramite un microcontrollore **Arduino UNO R4 WiFi**, li invia via connessione Seriale a un **Bridge Serial-MQTT** e li smista a un broker **Mosquitto**. Un **Data Collector** cloud in Python elabora i dati, gestisce il *Digital Twin* della pianta su file JSON, valuta le policy decisionali ed aziona la pompa di irrigazione. Un backend in **Flask** espone le API REST consumate da una dashboard web moderna sviluppata in **Next.js** e **React**.



## Caratteristiche Principali

* **Monitoraggio Real-Time**: Acquisizione continua dei valori di umidità relativa del terreno tramite sensore capacitivo.
* **Irrigazione Automatica a Policy**: Attivazione e disattivazione automatica della pompa idrica in base a regole di soglia definite in formato JSON (`policy\_conf.json`).
* **Controllo Manuale da Remoto**: Interfaccia grafica interattiva con pulsanti di avvio/arresto rapido dell'irrigazione via HTTP REST e MQTT.
* **Feedback Visivo Hardware**: Animazioni dinamiche sulla matrice LED integrata di Arduino UNO R4 ("smile" in standby, "goccia" durante l'irrigazione).
* **Digital Twin \& Persistenza JSON**: Modellazione digitale dello stato del vaso con salvataggio dello storico misurazioni ed azioni degli attuatori.
* **Architettura Modulare \& Disaccoppiata**: Implementazione basata sul pattern Publish/Subscribe (MQTT) con separazione netta tra logica hardware, data collector, backend e frontend.


## 🏗️ Architettura del Sistema

Il flusso informativo collega l'ambiente fisico al Cloud e alla Web App tramite la seguente catena:

```
\[Sensore Capacitivo / Relè + Pompa]
                │
         (Cavo analogico/digitale)
                ▼
      \[Arduino UNO R4 WiFi]
                │
          (Cavo USB / Seriale 9600 baud)
                ▼
      \[Bridge Serial-MQTT]
                │
          (Protocollo MQTT / TCP 7883)
                ▼
      \[Broker MQTT Mosquitto (Docker)]
                │
          (Protocollo MQTT)
                ▼
      \[Data Collector (Consumer / Producer / Policy Manager)]
                │
          (Scrittura/Lettura File JSON)
                ▼
      \[Backend REST API (Flask)]
                │
          (Richieste HTTP / JSON)
                ▼
      \[Frontend Web App (Next.js 14 / React / Recharts)]

```


## 🔌 Architettura Hardware e Circuiti

### Componenti Utilizzati

|Componente|Modello / Specifiche|Ruolo nel Sistema|
|-|-|-|
|**Microcontrollore**|Arduino UNO R4 WiFi (Renesas RA4M1 32-bit + ESP32-S3)|Acquisizione sensori, controllo relè e matrice LED|
|**Sensore Umidità**|Sensore Capacitivo di Umidità del Suolo|Misurazione dell'umidità del terreno senza corrosione|
|**Attuatore**|Modulo Relè 5V Low-Level Trigger|Interruttore di potenza per l'alimentazione della pompa|
|**Pompa Idrica**|Mini pompa ad immersione DC 3V–4.5V (Portata \~100 L/h)|Pescaggio acqua dal serbatoio ed irrigazione del vaso|
|**Alimentazione Pompa**|Porta-pile esterno 3V (2x pile AA 1.5V)|Alimentazione separata per evitare picchi di assorbimento su Arduino|

### Schema dei Collegamenti

|Dispositivo|Pin Componente|Collegamento ad Arduino / Circuito|
|-|-|-|
|**Sensore Capacitivo**|VCC / GND / AUOUT|5V Arduino / GND Arduino / **A0** Arduino|
|**Modulo Relè**|VCC / GND / IN|5V Arduino / GND Arduino / **Pin D7** Arduino|
|**Circuito Potenza Pompa**|Relè COM / Relè NO|**+ 3V** Alimentatore Esterno / **+ (Rosso)** Pompa|
|**Massa Comune**|**- (Nero)** Pompa / GND|**- 3V** Alimentatore Esterno / **GND** Arduino|


## 📡 Protocolli di Comunicazione e Topic MQTT

### 1\. Protocollo Seriale (Arduino ↔ Bridge)

* **Baud Rate**: `9600`
* **Pacchetto Dati Sensori (Arduino ➔ Bridge)**:
`0xFF <ID\_SENSORE> <TIPO\_SENSORE> <VALORE\_NORMALIZZATO> 0xFE`
* *Esempio*: `0xFF 0x01 'H' 0x4B 0xFE` (Umidità 'H', valore normalizzato a 75).



* **Comandi Attuatori (Bridge ➔ Arduino)**:
`<TIPO\_ATTUATORE> <COMANDO>`
* `'I'` + `'A'`: Attiva irrigazione (pin D7 LOW, relè acceso).
* `'I'` + `'S'`: Disattiva irrigazione (pin D7 HIGH, relè spento).



### 2\. Topic MQTT (Bridge ↔ Broker ↔ Data Collector)

* **Telemetria Sensori**: `plant/sensor/humidity` (QoS 0)
* **Comandi Attuatori**: `plant/actuator/irrigation` (Payload: `start` / `stop`)



## 💻 Moduli Software

### 1\. Bridge Serial-MQTT (`bridge\_Serial\_MQTT.py`)

Legge la porta seriale locale connessa ad Arduino, accumula i byte fino al carattere di fine pacchetto `0xFE`, converte il dato ed effettua la `publish` sul broker MQTT. Contestualmente si iscrive ai topic dei comandi ed inoltra i segnali ad Arduino.

### 2\. Data Collector Python (`data\_collector/`)

* **`Factory`**: Istanzia i descrittori delle piante leggendo il file `plants\_config.json`.
* **`DataCollectorConsumer`**: Riceve i dati di telemetria via MQTT, aggiorna il registro JSON ed invoca il Policy Manager.
* **`PolicyManager`**: Confronta i valori misurati con le regole attive in `policy\_conf.json`.
* **`DataCollectorProducer`**: Invia i comandi di attivazione/spegnimento della pompa sul topic MQTT dell'attuatore.
* **`JsonManager`**: Gestisce la lettura/scrittura atomica dei file JSON contenenti lo storico temporale.

### 3\. Backend REST API (`web\_api\_server.py`)

Server web Flask che legge il Digital Twin nei file JSON e mette a disposizione le rotte HTTP per il frontend:

|Metodo|Endpoint|Descrizione|
|-|-|-|
|`GET`|`/api/plants`|Restituisce la lista di tutte le piante e il loro stato attuale|
|`GET`|`/api/plants/<id>`|Dettagli completi e letture per una singola pianta|
|`POST`|`/api/plants/<id>/actuators/<tipo>`|Invia un comando all'attuatore (es. `{"action": "start"}`)|
|`GET`|`/api/plants/<id>/sensors/<tipo>/history`|Storico delle letture filtrate nel tempo|
|`GET`|`/api/health`|Healthcheck del server|
|`GET`|`/api/stats`|Statistiche aggregate (umidità media, irrigazioni attive)|

### 4\. Frontend Web (`dashboard/`)

Dashboard sviluppata con **Next.js 14**, **React**, **TypeScript**, **Tailwind CSS** e **Recharts**:

* **Card Pianta**: Mostra la specie, l'immagine dedicata, l'umiditàattuale e il timestamp dell'ultima irrigazione.
* **Grafico Dinamico**: Rappresentazione temporale dell'andamento dell'umidità.
* **Controlli Manuali**: Pulsante Play/Stop per attivare/arrestare manualmente la pompa con feedback in tempo reale.
* **Polling Automatico**: Aggiornamento periodico dell'interfaccia ogni 10 secondi.


## 📂 Struttura del Repository

```
Plants-System/
├── 📁 cloud\_simulator/           # Persistenza dati e simulazione Cloud
│   └── 📁 plants\_log/            # File JSON del Digital Twin (es. my\_felce.json)
├── 📁 dashboard/                 # Frontend Next.js \& Server Flask REST API
│   ├── 📁 app/                   # Pagine e routing Next.js (page.tsx)
│   ├── 📁 components/            # Componenti React UI (plant-dashboard.tsx, etc.)
│   ├── 📁 lib/                   # Client API (api.ts)
│   └── 📄 web\_api\_server.py      # Server REST API Flask
├── 📁 data\_collector/            # Unità di Elaborazione e Controllo Policy
│   ├── 📄 data\_collector\_main.py # Main orchestratore dei Consumer/Producer
│   ├── 📄 data\_collector\_consumer.py
│   ├── 📄 data\_collector\_producer.py
│   ├── 📄 policy\_manager.py      # Gestore regole ed automazioni
│   ├── 📄 json\_manager.py        # Gestione lettura/scrittura file JSON
│   └── 📁 factory/               # Factory per creazione PlantDescriptor
├── 📁 mqtt\_broker/               # Configurazione del Broker MQTT Mosquitto
│   ├── 📄 docker-compose.yml
│   └── 📄 mosquitto.conf
├── 📁 bridge/                    # Bridge di comunicazione locale
│   └── 📄 bridge\_Serial\_MQTT.py  # Bridge Seriale ↔ MQTT
└── 📁 arduino/                   # Codice C++ per Arduino UNO R4 WiFi
    └── 📄 smart\_pot.ino          # Firmware Arduino (Sensore + Relè + Matrice LED)

```

## ⚙️ Configurazione

### Configurazione Piante (`plants\_config.json`)

```json
{
  "plants": \[
    {
      "plant\_id": "my\_felce",
      "species": "Pteridofite",
      "description": "Pianta Felce",
      "sensors": \[
        {
          "humidity": {
            "enabled": true,
            "initial\_value": 80.0,
            "unit": "%",
            "min\_value": 50.0,
            "max\_value": 150.0,
            "is\_real": true
          }
        }
      ],
      "actuators": \[
        {
          "irrigation": {
            "enabled": true,
            "is\_real": true
          }
        }
      ]
    }
  ]
}

```

### Regole di Automazione (`policy\_conf.json`)

```json
\[
  {
    "plant\_id": "my\_felce",
    "policies": \[
      {
        "sensor": "humidity",
        "condition": "<",
        "value": 75,
        "action": "activate",
        "actuator": "irrigation"
      },
      {
        "sensor": "humidity",
        "condition": ">",
        "value": 90,
        "action": "deactivate",
        "actuator": "irrigation"
      }
    ]
  }
]

```

\---

## 🚀 Installazione e Avvio

### Prerequisiti

* **Python 3.8+**
* **Node.js 18+** e **npm**
* **Docker \& Docker Compose**
* **Arduino IDE** (per caricare lo sketch sulla scheda)

### 1\. Clonare il Repository

```bash
git clone https://github.com/yourusername/Plants-System.git
cd Plants-System

```

### 2\. Caricare lo Sketch su Arduino

Apri il file `arduino/sensor_actuator.ino` nell'Arduino IDE, seleziona la scheda **Arduino UNO R4 WiFi** e la porta COM corretta, quindi effettua il caricamento.

### 3\. Avviare il Broker MQTT (Docker)

```bash
cd mqtt\_broker
docker-compose up -d
cd ..

```

### 4\. Installare le Dipendenze Python

```bash
pip install -r requirements.txt

```

### 5\. Avviare il Bridge Serial-MQTT

```bash
python bridge/bridge\_Serial\_MQTT.py

```

### 6\. Avviare il Data Collector

In un nuovo terminale:

```bash
python data\_collector/data\_collector\_main.py

```

### 7\. Avviare il Backend Flask REST API

In un nuovo terminale:

```bash
python dashboard/web\_api\_server.py

```

### 8\. Installare ed Avviare il Frontend Next.js

In un nuovo terminale:

```bash
cd dashboard
npm install
npm run dev

```

Visita **`http://localhost:3000`** nel browser per accedere alla dashboard.


## 🔮 Sviluppi Futuri

* **Sensori Aggiuntivi**: Integrazione di sensori di luminosità, temperatura ambientale e pH del terreno.
* **Gestione Utenti e Notifiche Push**: Sistema di autenticazione e notifiche su smartphone per avvisi su serbatoio vuoto o anomalie.
* **Interfaccia Grafica per Policy**: Modifica dinamica delle regole di irrigazione dalla dashboard senza modificare file JSON.
* **Algoritmi Predittivi ML**: Utilizzo di modelli di Machine Learning per ottimizzare i consumi d'acqua in base alle condizioni meteo e alla specie vegetale.
* **Supporto Multi-Vaso**: Gestione centralizzata di più vasi con risorse e serbatoi condivisi.


## 🎓 Contesto Accademico

Questo prototipo è stato sviluppato all'interno del corso di Internet of Things, erogato dall'Università degli Studi di Modena e Reggio Emilia (UNIMORE) e come elaborato finale.

## 📄 Licenza

Distribuito sotto licenza MIT. Vedi `LICENSE` per maggiori informazioni.

