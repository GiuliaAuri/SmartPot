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

Il sistema è composto da tre componenti principali:

### 🔧 Backend (Python/Flask)
- **API REST** per gestione dati e comandi
- **Data Collector** per raccolta dati MQTT
- **Policy Manager** per valutazione automatica
- **Gestione File JSON** per persistenza dati

### 🎨 Frontend (Next.js/React)
- **Dashboard Interattiva** per monitoraggio real-time
- **Configurazione Policy** per personalizzazione
- **Gestione Alert** per notifiche utente
- **Monitoraggio Storico** con grafici

### 🌐 Comunicazione MQTT
- **Broker Mosquitto** per messaggistica
- **Producer/Consumer** per telemetria e comandi
- **Topic Strutturati** per organizzazione dati

### 📊 Funzionalità Principali

- **Monitoraggio Real-time**: Visualizzazione continua di tutti i parametri
- **Irrigazione Automatica**: Attivazione basata su policy configurabili
- **Sistema di Alert**: Notifiche per batteria bassa, livello acqua, anomalie
- **Gestione Multi-pianta**: Supporto per più piante simultaneamente
- **Configurazione Flessibile**: Policy personalizzabili per tipo di pianta
- **Persistenza Dati**: Salvataggio storico per analisi e debugging

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

Per scoprire quali piante sono disponibili nel sistema, ci si sottoscrive al topic:
```
plant/+/info
```
## 💧 Attuatore per l’Irrigazione

L’attuatore che gestisce l’irrigazione non pubblica dati, ma è **sottoscritto** a un topic dedicato ai comandi:
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
cd dashboard
npm install
```

### 4. Avviare MQTT Broker
```bash
cd mqtt_broker
docker-compose up -d
```

### 5. Avviare il Sistema
```bash
# Terminal 1: Backend
python dashboard/app.py

# Terminal 2: Frontend
cd dashboard
npm run dev

# Terminal 3: Simulazione Piante
python plants_system/process/plant_main.py

# Terminal 4: Data Collector
python plants_system/process/data_collector_main.py
```

## 📁 Struttura del Progetto

```
Plants-System/
├── 📁 dashboard/                 # Frontend Next.js
│   ├── 📁 app/                   # Pagine applicazione
│   ├── 📁 components/            # Componenti React
│   ├── 📁 lib/                   # Utilities e API
│   ├── 📁 managers/              # Gestori dati
│   ├── 📁 processors/            # Elaboratori dati
│   ├── 📁 routes/                # Route API Flask
│   └── 📁 utils/                 # Funzioni di utilità
├── 📁 plants_system/             # Backend Python
│   ├── 📁 process/               # Processi principali
│   ├── 📁 smart_objects/         # Sensori e attuatori
│   └── 📁 resources/             # Configurazioni
├── 📁 mqtt_broker/               # Configurazione MQTT
├── 📁 cloud_simulator/           # Simulazione dati
└── 📁 tests/                     # Test unitari
```

## 🔧 Configurazione

### Policy di Irrigazione
Le policy sono configurabili nel file `plants_system/smart_objects/resources/policies_conf.json`:

```json
{
  "plant_id": "plant_cactus_001",
  "policies": [
    {
      "sensor": "humidity",
      "condition": "<",
      "value": 30,
      "action": "activate",
      "actuator": "irrigation",
      "message": "Umidità bassa - Attivazione irrigazione"
    }
  ]
}
```

### Configurazione Piante
Le piante sono definite in `plants_system/smart_objects/resources/plants_config.json`:

```json
[
  {
    "plant_id": "plant_cactus_001",
    "species": "Cactus"
  }
]
```

## 📊 Monitoraggio

### Dashboard Web
- **URL**: http://localhost:3000
- **Monitoraggio Real-time**: Visualizzazione dati live
- **Configurazione**: Gestione policy e alert
- **Storico**: Grafici e trend temporali

### API Endpoints
- `GET /api/plants` - Lista tutte le piante
- `GET /api/alerts` - Alert attivi
- `POST /api/plants/{id}/actuator/{actuator}` - Controllo attuatori
- `GET /api/status` - Stato sistema

## 🔄 Flusso di Dati

```
🌱 Sensori → 📡 MQTT → 📊 Data Collector → 💾 JSON Files → 🌐 API → 🎨 Frontend
     ↓              ↓           ↓              ↓           ↓         ↓
  Telemetria    Broker      Elaborazione    Persistenza   REST    Dashboard
```

## 🛠️ Sviluppo

### Aggiungere Nuovo Sensore
1. Creare classe in `plants_system/smart_objects/sensors/`
2. Ereditare da `Sensor[T]`
3. Implementare metodo `update()`
4. Aggiungere al dispositivo appropriato

### Aggiungere Nuovo Attuatore
1. Creare classe in `plants_system/smart_objects/actuators/`
2. Ereditare da `SwitchActuator`
3. Implementare logica di controllo
4. Aggiungere al dispositivo appropriato

## 📝 Log e Debugging

I log sono configurati per diversi livelli:
- **INFO**: Operazioni normali
- **DEBUG**: Dettagli tecnici
- **WARNING**: Situazioni anomale
- **ERROR**: Errori critici

## 🤝 Contribuire

1. Fork del repository
2. Creare branch feature (`git checkout -b feature/AmazingFeature`)
3. Commit delle modifiche (`git commit -m 'Add AmazingFeature'`)
4. Push al branch (`git push origin feature/AmazingFeature`)
5. Aprire Pull Request

## 📄 Licenza

Distribuito sotto licenza MIT. Vedi `LICENSE` per maggiori informazioni.


