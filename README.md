# 🌱 Plants-System

## Smart Home - Sistema IoT per Gestione Intelligente delle Piante

[![Python](https://img.shields.io/badge/Python-3.8+-blue.svg)](https://python.org)
[![Flask](https://img.shields.io/badge/Flask-2.0+-green.svg)](https://flask.palletsprojects.com)
[![Next.js](https://img.shields.io/badge/Next.js-13+-black.svg)](https://nextjs.org)
[![MQTT](https://img.shields.io/badge/MQTT-Mosquitto-orange.svg)](https://mosquitto.org)
[![License](https://img.shields.io/badge/License-MIT-yellow.svg)](LICENSE)

## 📋 Descrizione

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
## 🏗️ Architettura del Sistema

Il sistema è composto da cinque componenti principali:

### 🔧 Backend (Python/Flask)
- **API REST** (`backend/web_api_server.py`) per gestione dati e comandi
- **Endpoints** per controllo irrigazione, recupero dati sensori e stato piante

### 📊 Data Collector (Python)
- **Data Collector Consumer** (`data_collector/data_collector_consumer.py`) per raccolta dati MQTT
- **Data Collector Producer** (`data_collector/data_collector_producer.py`) per invio comandi
- **Policy Manager** (`data_collector/policy_manager.py`) per valutazione automatica
- **Factory** (`data_collector/factory/`) per configurazione piante
- **JSON Manager** per persistenza dati in `cloud_simulator/plants_log/`

### 🎨 Frontend (Next.js/React/TypeScript)
- **Dashboard Interattiva** (`frontend/app/page.tsx`) per monitoraggio real-time
- **Componenti React** (`frontend/components/`) per visualizzazione dati
- **UI moderna** con shadcn/ui e Tailwind CSS
- **Grafici in tempo reale** con Recharts

### 🌐 Bridge Arduino-MQTT (Python)
- **Bridge Serial-MQTT** (`bridge/bridge_Serial_MQTT.py`) per comunicazione con Arduino
- **Traduzione** tra protocollo seriale e MQTT

### 🤖 Arduino/Simulazione
- **Firmware Arduino** (`arduino/sensor_actuator.ino`) per sensori e attuatori reali
- **Simulazione sensori/attuatori** (`smart_objects/`) in Python

### 📊 Funzionalità Principali

- **Monitoraggio Real-time**: Visualizzazione continua di umidità del terreno
- **Irrigazione Automatica**: Attivazione basata su policy configurabili
- **Gestione Multi-pianta**: Supporto per più piante simultaneamente
- **Configurazione Flessibile**: Policy personalizzabili in `data_collector/policies/policies_conf.json`
- **Persistenza Dati**: Salvataggio storico JSON per analisi
- **Supporto Arduino**: Integrazione con hardware reale tramite bridge seriale

## 🌱 Sensori di Telemetria

I sensori disponibili nel sistema sono implementati in `smart_objects/sensors/`:

- **Umidità del terreno** (`humidity_sensor.py`) - Monitoraggio umidità suolo
- **Temperatura** (`temperature_sensor.py`) - Temperatura ambiente
- **Luminosità** (`lightness_sensor.py`) - Livello di luce
- **Livello batteria** (`battery_level_sensor.py`) - Stato batteria dispositivo
- **Livello serbatoio** (`level_tank_sensor.py`) - Livello acqua nel serbatoio
- **Flusso acqua** (`water_flow_sensor.py`) - Consumo acqua in l/s

I sensori possono essere:
- **Simulati** in software Python
- **Reali** tramite Arduino collegato via bridge seriale

I dati raccolti vengono **pubblicati** sul topic MQTT con la seguente struttura: 
```
 plant/{plant_id}/device/{device_id}/telemetry/{resource_id}
```

Per scoprire quali piante sono disponibili nel sistema, ci si sottoscrive al topic:
```
plant/+/info
```
## 💧 Attuatore per l'Irrigazione

L'attuatore di irrigazione è implementato in `smart_objects/actuators/irrigation_actuator.py`.

Funzionamento:
- È **sottoscritto** al topic MQTT per ricevere comandi
- Può essere controllato tramite **API REST** (`POST /api/plants/{plant_id}/actuator/irrigation`)
- Può essere **manuale** (controllato dall'utente) o **automatico** (basato su policy)

Topic MQTT per i comandi:
```
plant/{plant_id}/device/{device_id}/command/{resource_id}
```


## 🚀 Installazione e Avvio

### Prerequisiti
- Python 3.8+
- Node.js 16+
- Docker (per MQTT Broker)

### 1. Clonare il Repository
```bash
git clone https://github.com/yourusername/Plants-System.git
cd Plants-System
```

### 2. Installare Dipendenze Backend
```bash
pip install -r requirements.txt
```

### 3. Installare Dipendenze Frontend
```bash
cd frontend
npm install
```

### 4. Avviare MQTT Broker
```bash
cd mqtt_broker
docker-compose up -d
```

### 5. Avviare il Sistema

#### Opzione A: Sistema con Arduino Reale
```bash
# Terminal 1: Backend API
python backend/web_api_server.py

# Terminal 2: Data Collector
python data_collector/data_collector_main.py

# Terminal 3: Bridge Arduino-MQTT
python bridge/bridge_Serial_MQTT.py

# Terminal 4: Frontend
cd frontend
npm run dev
```

#### Opzione B: Sistema con Sensori Simulati
```bash
# Terminal 1: Backend API
python backend/web_api_server.py

# Terminal 2: Data Collector
python data_collector/data_collector_main.py

# Terminal 3: Simulazione Sensori
python tests/simulate_arduino.py
# oppure
python tests/test_complete_system.py

# Terminal 4: Frontend
cd frontend
npm run dev
```

### 6. Accedere alla Dashboard
Aprire il browser all'indirizzo: **http://localhost:3000**

## 📁 Struttura del Progetto

```
Plants-System/
├── 📁 backend/                      # Backend Flask API
│   └── web_api_server.py            # Server API REST
├── 📁 frontend/                     # Frontend Next.js
│   ├── 📁 app/                      # Pagine Next.js
│   │   ├── page.tsx                 # Pagina principale dashboard
│   │   └── layout.tsx               # Layout applicazione
│   ├── 📁 components/               # Componenti React
│   │   ├── plant-dashboard.tsx      # Dashboard piante (UTILIZZATO)
│   │   ├── alerts-panel.tsx         # Pannello avvisi (non utilizzato)
│   │   ├── humidity-chart.tsx       # Grafico umidità avanzato (non utilizzato)
│   │   ├── plant-configuration.tsx  # Config avanzata (non utilizzato)
│   │   ├── real-time-monitoring.tsx # Monitoring avanzato (non utilizzato)
│   │   ├── theme-provider.tsx       # Gestione temi (non utilizzato)
│   │   └── 📁 ui/                   # Componenti UI (shadcn/ui)
│   └── 📁 lib/                      # Utilities e API client
│       └── api.ts                   # Client API REST
├── 📁 data_collector/               # Sistema raccolta dati
│   ├── data_collector_main.py       # Entry point collector
│   ├── data_collector_consumer.py   # Consumer MQTT
│   ├── data_collector_producer.py   # Producer MQTT
│   ├── policy_manager.py            # Gestione policy
│   ├── json_manager.py              # Persistenza JSON
│   ├── plant_descriptor.py          # Descrittore pianta
│   ├── 📁 factory/                  # Factory piante
│   │   ├── factory.py               # Factory pattern
│   │   └── plants_config.json       # Config piante
│   └── 📁 policies/                 # Policy di irrigazione
│       └── policies_conf.json       # Configurazione policy
├── 📁 bridge/                       # Bridge Arduino-MQTT
│   ├── bridge_Serial_MQTT.py        # Bridge seriale/MQTT
│   └── config.ini                   # Configurazione bridge
├── 📁 arduino/                      # Firmware Arduino
│   └── sensor_actuator.ino          # Sketch Arduino
├── 📁 smart_objects/                # Sensori e attuatori simulati
│   ├── 📁 sensors/                  # Implementazione sensori
│   │   ├── humidity_sensor.py       # Sensore umidità
│   │   ├── temperature_sensor.py    # Sensore temperatura
│   │   ├── lightness_sensor.py      # Sensore luminosità
│   │   ├── battery_level_sensor.py  # Sensore batteria
│   │   ├── level_tank_sensor.py     # Sensore livello
│   │   └── water_flow_sensor.py     # Sensore flusso
│   ├── 📁 actuators/                # Implementazione attuatori
│   │   └── irrigation_actuator.py   # Attuatore irrigazione
│   └── 📁 models/                   # Modelli base
│       ├── Sensor.py                # Classe base sensore
│       └── SwitchActuator.py        # Classe base attuatore
├── 📁 mqtt_broker/                  # Broker MQTT
│   ├── docker-compose.yml           # Config Docker Mosquitto
│   └── 📁 mosquitto/                # Config Mosquitto
├── 📁 cloud_simulator/              # Persistenza dati
│   └── 📁 plants_log/               # Log JSON piante
│       └── my_felce.json            # Dati storici pianta
├── 📁 conf/                         # Configurazioni globali
│   └── mqtt_conf_params.py          # Parametri MQTT
├── 📁 tests/                        # Test e simulazioni
│   ├── test_complete_system.py      # Test sistema completo
│   ├── simulate_arduino.py          # Simulazione Arduino
│   └── ...                          # Altri test
├── 📁 doc/                          # Documentazione
│   ├── SYSTEM_DOCUMENTATION.md      # Doc sistema
│   ├── WEB_DASHBOARD_README.md      # Doc dashboard
│   └── ...                          # Altri doc
├── README.md                        # Questo file
└── requirements.txt                 # Dipendenze Python
```

## 🔧 Configurazione

### Policy di Irrigazione
Le policy sono configurabili nel file `data_collector/policies/policies_conf.json`:

```json
[
  {
    "plant_id": "my_felce",
    "policies": [
      {
        "sensor": "humidity",
        "condition": "<",
        "value": 75,
        "actuator": "irrigation",
        "action": "activate"
      },
      {
        "sensor": "humidity",
        "condition": ">",
        "value": 90,
        "actuator": "irrigation",
        "action": "deactivate"
      }
    ]
  }
]
```

### Configurazione Piante
Le piante sono definite in `data_collector/factory/plants_config.json`:

```json
{
  "plants": [
    {
      "plant_id": "my_felce",
      "species": "Pteridofite",
      "description": "Pianta Felce",
      "sensors": [{
        "humidity": {
          "enabled": true,
          "initial_value": 80.0,
          "unit": "%",
          "min_value": 50.0,
          "max_value": 150.0,
          "is_real": true
        }
      }],
      "actuators": [{
        "irrigation": {
          "enabled": true,
          "is_real": true
        }
      }]
    }
  ]
}
```

## 📊 Monitoraggio

### Dashboard Web
- **URL**: http://localhost:3000
- **Monitoraggio Real-time**: Visualizzazione umidità e stato irrigazione
- **Aggiornamento automatico**: Polling ogni 10 secondi
- **Controllo manuale**: Pulsanti start/stop irrigazione
- **Grafici**: Andamento umidità ultime 24 ore
- **Responsive**: Design adattivo mobile/tablet/desktop

### API Endpoints (Backend Flask)
Server in ascolto su **http://localhost:5000**

- `GET /api/plants` - Lista tutte le piante con sensori e attuatori
- `GET /api/plants/{plant_id}` - Dettagli pianta specifica
- `GET /api/plants/{plant_id}/sensors/{sensor_type}` - Valore sensore corrente
- `GET /api/plants/{plant_id}/sensors/{sensor_type}/history?hours=24` - Storico sensore
- `POST /api/plants/{plant_id}/actuator/{actuator_name}` - Controllo attuatore
  - Body: `{"action": "start"}` o `{"action": "stop"}`
- `GET /api/status` - Stato generale del sistema

## 🔄 Flusso di Dati

### Telemetria (Sensori → Frontend)
```
Arduino/Simulazione → Bridge/MQTT → Data Collector Consumer → JSON Files → API Flask → Frontend
   
```

### Comandi (Frontend → Attuatori)
```
Frontend → API Flask → Data Collector Producer → MQTT → Bridge/Arduino → Attuatori

```

### Policy Automatiche
```
Data Collector Consumer → Policy Manager → Valutazione condizioni → Data Collector Producer → Attuatori

```

## 🛠️ Sviluppo

### Aggiungere Nuovo Sensore
1. Creare classe in `smart_objects/sensors/`
2. Ereditare da `Sensor[T]` (da `smart_objects/models/Sensor.py`)
3. Implementare metodo `update()` per simulazione valori
4. Aggiungere sensore in `data_collector/factory/plants_config.json`
5. Implementare supporto in Arduino se necessario (`arduino/sensor_actuator.ino`)

### Aggiungere Nuovo Attuatore
1. Creare classe in `smart_objects/actuators/`
2. Ereditare da `SwitchActuator` (da `smart_objects/models/SwitchActuator.py`)
3. Implementare logica di controllo (activate/deactivate)
4. Aggiungere attuatore in `data_collector/factory/plants_config.json`
5. Aggiungere endpoint API in `backend/web_api_server.py`
6. Implementare supporto in Arduino se necessario

### Aggiungere Nuova Policy
1. Modificare `data_collector/policies/policies_conf.json`
2. Aggiungere condizione con sensor, condition, value, actuator, action
3. Il `policy_manager.py` valuterà automaticamente la nuova policy

## 📝 Log e Debugging

### File di Log
- `mqtt_broker/mosquitto/log/mosquitto.log` - Log broker MQTT
- `cloud_simulator/plants_log/` - Dati storici piante in formato JSON
- Console output dei vari componenti (backend, data collector, bridge)

### Livelli di Log
- **INFO**: Operazioni normali
- **DEBUG**: Dettagli tecnici (telemetria, comandi MQTT)
- **WARNING**: Situazioni anomale
- **ERROR**: Errori critici

### Debug Utili
```bash
# Monitorare messaggi MQTT in tempo reale
mosquitto_sub -h localhost -t 'plant/#' -v

# Verificare stato broker
docker logs mqtt_broker

# Verificare API
curl http://localhost:5000/api/status
```

## ⚠️ Note sullo Sviluppo

### Componenti Frontend Non Utilizzati
Il progetto include alcuni componenti React avanzati non ancora integrati nel sistema:
- `alerts-panel.tsx` - Sistema completo di gestione avvisi
- `humidity-chart.tsx` - Grafico umidità con selezione periodo (24h/7gg)
- `plant-configuration.tsx` - Configurazione avanzata policy per pianta
- `real-time-monitoring.tsx` - Dashboard avanzata con grafici multipli
- `theme-provider.tsx` - Supporto tema scuro/chiaro

Questi componenti sono funzionali e pronti per l'integrazione in future versioni.

### Documentazione Aggiuntiva
Per dettagli specifici consulta:
- `doc/SYSTEM_DOCUMENTATION.md` - Documentazione architettura
- `doc/WEB_DASHBOARD_README.md` - Guida dashboard web
- `doc/MANUAL_CONTROL_README.md` - Controllo manuale irrigazione
- `doc/TEST_BRIDGE_README.md` - Test bridge Arduino

## 🤝 Contribuire

1. Fork del repository
2. Creare branch feature (`git checkout -b feature/AmazingFeature`)
3. Commit delle modifiche (`git commit -m 'Add AmazingFeature'`)
4. Push al branch (`git push origin feature/AmazingFeature`)
5. Aprire Pull Request

## 📄 Licenza

Distribuito sotto licenza MIT. Vedi `LICENSE` per maggiori informazioni.

