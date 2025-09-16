# Plants-System: Documentazione Completa del Sistema

## 📋 Indice
1. [Panoramica del Sistema](#panoramica-del-sistema)
2. [Architettura Generale](#architettura-generale)
3. [Flusso Operativo](#flusso-operativo)
4. [Classi e Componenti](#classi-e-componenti)
5. [Configurazione](#configurazione)
6. [Esempi di Utilizzo](#esempi-di-utilizzo)

---

## 🌱 Panoramica del Sistema

Il **Plants-System** è un sistema IoT completo per il monitoraggio e controllo intelligente di piante. Il sistema integra:

- **Sensori simulati e reali** (temperatura, umidità, luminosità, ecc.)
- **Attuatori** (irrigazione automatica)
- **Comunicazione MQTT** per la distribuzione dei dati
- **Bridge Arduino** per sensori fisici
- **Dashboard web** per visualizzazione e controllo
- **Policy engine** per automazione intelligente

---

## 🏗️ Architettura Generale

```
┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐
│   Arduino        │    │   Plants-System │    │   Dashboard     │
│   (Sensori       │◄──►│   (Core System)  │◄──►│   (Frontend)    │
│   Fisici)        │    │                 │    │                 │
└─────────────────┘    └─────────────────┘    └─────────────────┘
         │                       │                       │
         │                       │                       │
         ▼                       ▼                       ▼
┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐
│   Serial        │    │   MQTT Broker   │    │   File JSON     │
│   Communication │    │   (Mosquitto)   │    │   (Data Store)  │
└─────────────────┘    └─────────────────┘    └─────────────────┘
```

---

## 🔄 Flusso Operativo

### 1. **Inizializzazione del Sistema**
```
plant_main.py → Carica configurazione → Crea piante → Avvia thread
```

### 2. **Raccolta Dati Sensori**
```
Sensori (Simulati/Reali) → PlantProducer → MQTT → DataCollectorConsumer → File JSON
```

### 3. **Controllo Attuatori**
```
Dashboard/Policy → PlantConsumer → MQTT → Attuatori → Arduino (se reale)
```

### 4. **Integrazione Arduino**
```
Arduino → Bridge → Sensori Reali → MQTT → File JSON → Dashboard
```

---

## 🧩 Classi e Componenti

### **Core System Classes**

#### **1. PlantFactory** (`plants_system/smart_objects/resources/factory_plants.py`)
**Scopo**: Factory per la creazione di oggetti PlantDescriptor

**Comportamento**:
- Carica configurazione da `plants_config.json`
- Crea istanze di `PlantDescriptor` per ogni pianta
- Istanzia dispositivi (`EnvironmentTelemetryData`, `TankMonitoring`, `WaterMetering`)
- Gestisce sensori e attuatori basati su configurazione

**Metodi Principali**:
```python
create_plants_from_json(json_path)  # Crea tutte le piante dal file JSON
_create_plant_from_config(config)   # Crea una singola pianta
```

#### **2. PlantDescriptor** (`plants_system/smart_objects/models/plant_descriptor.py`)
**Scopo**: Rappresenta una singola pianta con i suoi dispositivi

**Comportamento**:
- Contiene informazioni base (ID, specie, descrizione)
- Gestisce lista di dispositivi associati
- Serializza dati in formato JSON per MQTT

**Struttura**:
```python
class PlantDescriptor:
    plant_id: str           # Identificatore univoco
    species: str            # Tipo di pianta (cactus, fico, ecc.)
    devices: List[Device]   # Lista dispositivi (sensori + attuatori)
```

#### **3. Device Classes**

##### **EnvironmentTelemetryData** (`plants_system/smart_objects/devices/environment_telemetry.py`)
**Scopo**: Gestisce sensori ambientali

**Sensori Gestiti**:
- `TemperatureSensor`: Temperatura ambiente (-10°C a 50°C)
- `HumiditySensor`: Umidità relativa (0% a 100%)
- `LightnessSensor`: Luminosità (0 a 100000 lx)
- `BatteryLevelSensor`: Livello batteria (0% a 100%)

**Comportamento**:
- Carica configurazione sensori da `FactoryConfig`
- Crea sensori con valori iniziali e range specificati
- Distingue tra sensori simulati (`is_real=False`) e reali (`is_real=True`)

##### **TankMonitoring** (`plants_system/smart_objects/devices/tank_monitoring.py`)
**Scopo**: Monitora livello serbatoio acqua

**Sensori Gestiti**:
- `LevelTankSensor`: Livello serbatoio (0 a 2 litri)

##### **WaterMetering** (`plants_system/smart_objects/devices/water_metering.py`)
**Scopo**: Gestisce irrigazione e misurazione acqua

**Sensori/Attuatori**:
- `WaterFlowSensor`: Flusso acqua (0 a 5 l/s)
- `IrrigationActuator`: Controllo irrigazione (ON/OFF)

### **Sensor Classes**

#### **Sensor** (`plants_system/smart_objects/models/Sensor.py`)
**Scopo**: Classe base astratta per tutti i sensori

**Comportamento**:
- Gestisce valori, unità di misura, range min/max
- Distingue tra sensori simulati e reali
- Aggiorna valori con timestamp
- Serializza dati in JSON

**Metodi Principali**:
```python
update()                    # Aggiorna valore (simulato o reale)
update_simulated()          # Genera valore casuale nel range
update_real()               # Override per sensori reali
to_json()                   # Serializza in formato JSON
```

#### **Sensori Specifici**
Tutti i sensori ereditano da `Sensor` e implementano:
- **TemperatureSensor**: Range -10°C a 50°C
- **HumiditySensor**: Range 0% a 100%
- **LightnessSensor**: Range 0 a 100000 lx
- **BatteryLevelSensor**: Range 0% a 100% (decrementa nel tempo)
- **LevelTankSensor**: Range 0 a 2 litri
- **WaterFlowSensor**: Range 0 a 5 l/s

### **Actuator Classes**

#### **SwitchActuator** (`plants_system/smart_objects/models/SwitchActuator.py`)
**Scopo**: Classe base per attuatori on/off

**Comportamento**:
- Gestisce stato ON/OFF
- Riceve comandi via MQTT
- Distingue tra attuatori simulati e reali

**Metodi Principali**:
```python
change_status()             # Inverte stato
handle_command(command)     # Processa comando ("ACTIVATE"/"DEACTIVATE")
```

#### **IrrigationActuator** (`plants_system/smart_objects/actuators/irrigation_actuator.py`)
**Scopo**: Controllo sistema irrigazione

**Comportamento**:
- Eredita da `SwitchActuator`
- Gestisce attivazione/disattivazione irrigazione
- Integra con Arduino per controllo fisico

### **Process Classes**

#### **PlantProducer** (`plants_system/process/plant_producer.py`)
**Scopo**: Pubblica dati telemetrici via MQTT

**Comportamento**:
- Si connette al broker MQTT
- Pubblica informazioni pianta e dati sensori
- Esegue loop continuo ogni 10 secondi
- Gestisce disconnessioni e riconnessioni

**Flusso**:
```
PlantDescriptor → generate_telemetry() → MQTT Publish → Broker
```

#### **PlantConsumer** (`plants_system/process/plant_consumer.py`)
**Scopo**: Riceve comandi via MQTT

**Comportamento**:
- Si connette al broker MQTT
- Sottoscrive ai topic dei comandi
- Processa comandi per attuatori
- Gestisce comandi di controllo sistema

**Flusso**:
```
MQTT Broker → Topic Commands → PlantConsumer → Attuatori
```

#### **DataCollectorConsumer** (`plants_system/process/data_collector_consumer.py`)
**Scopo**: Raccoglie e persiste dati sensori

**Comportamento**:
- Riceve dati telemetrici via MQTT
- Salva dati nei file JSON (`cloud_simulator/plants_log/`)
- Valuta policy automatiche
- Gestisce alert e notifiche

**Flusso**:
```
MQTT Data → DataCollectorConsumer → File JSON → Dashboard
```

### **Bridge Classes**

#### **Bridge** (`bridge/bridge_Serial.py`)
**Scopo**: Comunicazione seriale con Arduino

**Comportamento**:
- Gestisce connessione seriale con Arduino
- Riceve dati sensori in formato protocollo personalizzato
- Converte valori Arduino (0-255) in valori reali
- Aggiorna sensori reali nel sistema piante
- Invia comandi ad attuatori Arduino

**Protocollo Serial**:
```
Arduino → Python:
0xFF [num_sensori] [tipo1] [valore1] [tipo2] [valore2] ... 0xFE

Python → Arduino:
'A' = Attiva attuatore
'S' = Spegni attuatore
```

**Conversione Valori**:
```python
temperature = (arduino_value * 60.0 / 255.0) - 10.0  # -10°C a 50°C
humidity = arduino_value * 100.0 / 255.0             # 0% a 100%
lightness = arduino_value * 100000.0 / 255.0         # 0 a 100000 lx
```

### **Configuration Classes**

#### **FactoryConfig** (`plants_system/smart_objects/resources/factory_config.py`)
**Scopo**: Gestisce configurazione centralizzata

**Comportamento**:
- Carica `plants_config.json` una sola volta
- Fornisce metodi per accedere configurazioni specifiche
- Gestisce cache per performance
- Evita import circolari

**Metodi Principali**:
```python
get_plant_config(plant_id)           # Configurazione pianta
get_device_config(plant_id, device)  # Configurazione dispositivo
get_sensor_config(plant_id, device, sensor)  # Configurazione sensore
get_actuator_config(plant_id, device, actuator)  # Configurazione attuatore
```

### **Main Classes**

#### **Plants** (`plants_system/process/plant_main.py`)
**Scopo**: Classe principale che coordina tutto il sistema

**Comportamento**:
- Carica configurazione e crea piante
- Avvia producer, consumer e bridge Arduino
- Gestisce thread e ciclo di vita
- Monitora stato sistema

**Flusso di Avvio**:
```
1. Carica plants_config.json
2. Crea PlantDescriptor per ogni pianta
3. Avvia PlantProducer (thread MQTT)
4. Avvia PlantConsumer (thread MQTT)
5. Avvia Bridge Arduino (thread Serial)
6. Monitora stato sistema
```

---

## ⚙️ Configurazione

### **File di Configurazione Principali**

#### **1. plants_config.json**
```json
{
  "plants": [
    {
      "plant_id": "my_cactus1",
      "species": "cactus",
      "devices": {
        "environment_telemetry": {
          "enabled": true,
          "sensors": {
            "temperature": {
              "enabled": true,
              "initial_value": 25.0,
              "unit": "°C",
              "min_value": -10.0,
              "max_value": 50.0,
              "is_real": false  // true per sensori Arduino
            }
          }
        }
      }
    }
  ]
}
```

#### **2. bridge/config.ini**
```ini
[Serial]
UseDescription = no
PortDescription = arduino
PortName = COM5

[MQTT]
Port = 7883
Broker = localhost
```

### **Configurazione Sensori Reali**
Per utilizzare sensori Arduino fisici:
1. Imposta `"is_real": true` nel `plants_config.json`
2. Collega Arduino alla porta seriale specificata
3. Avvia il sistema con `plant_main.py`

---

## 🚀 Esempi di Utilizzo

### **1. Avvio Sistema Completo**
```bash
# Avvia sistema completo (MQTT + Arduino)
python plants_system/process/plant_main.py
```

### **2. Solo Data Collection**
```bash
# Solo raccolta dati (senza producer)
python plants_system/process/data_collector_main.py
```

### **3. Solo Bridge Arduino**
```bash
# Solo comunicazione Arduino
python bridge/bridge_Serial.py
```

### **4. Dashboard Web**
```bash
# Avvia dashboard
cd dashboard
python app.py
```

---

## 📊 Flusso Dati Completo

### **Scenario 1: Sensori Simulati**
```
PlantDescriptor → PlantProducer → MQTT → DataCollectorConsumer → File JSON → Dashboard
```

### **Scenario 2: Sensori Arduino**
```
Arduino → Bridge → Sensori Reali → PlantProducer → MQTT → DataCollectorConsumer → File JSON → Dashboard
```

### **Scenario 3: Controllo Attuatori**
```
Dashboard → PlantConsumer → MQTT → Attuatori → Arduino (se reale)
```

---

## 🔧 Troubleshooting

### **Problemi Comuni**

1. **Sensori non aggiornati**:
   - Verifica `"is_real": true` in configurazione
   - Controlla connessione Arduino
   - Verifica porta seriale in `config.ini`

2. **MQTT non funziona**:
   - Verifica broker Mosquitto attivo
   - Controlla configurazione MQTT
   - Verifica connessione di rete

3. **Dashboard non mostra dati**:
   - Verifica file JSON in `cloud_simulator/plants_log/`
   - Controlla DataCollectorConsumer attivo
   - Verifica configurazione dashboard

---

## 📈 Monitoraggio Sistema

### **Log e Debug**
- **Log Level**: Configurabile per ogni componente
- **Stato Sistema**: Monitorato da `Plants.print_system_status()`
- **Connessioni**: Verificate automaticamente
- **Performance**: Thread separati per non bloccare sistema

### **Metriche Chiave**
- Numero piante attive
- Sensori reali vs simulati
- Thread attivi
- Connessioni MQTT/Serial
- File JSON aggiornati

---

Questo documento fornisce una panoramica completa del sistema Plants-System, dalle classi base al flusso operativo completo. Per dettagli specifici su implementazione, consultare il codice sorgente delle singole classi.
