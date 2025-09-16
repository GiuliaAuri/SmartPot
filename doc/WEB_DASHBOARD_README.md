# 🌱 Plants System - Web Dashboard

Sistema completo per il monitoraggio e controllo dell'irrigazione delle piante con dashboard web.

## 🏗️ Architettura del Sistema

```
Arduino/Sensori ↔ Bridge (Serial-MQTT) ↔ Data Collector ↔ Web API ↔ Frontend Dashboard
```

### Componenti:

1. **Arduino/Sensori** - Raccoglie dati umidità e controlla attuatori
2. **Bridge** (`bridge_Serial_MQTT.py`) - Converte serial ↔ MQTT
3. **Data Collector** (`data_collector_main.py`) - Processa dati e applica policy
4. **Web API** (`web_api_server.py`) - Espone dati via REST API
5. **Frontend** (`frontend/`) - Dashboard web Next.js

## 🚀 Avvio del Sistema

### 1. Avvia il Data Collector
```bash
python data_collector/data_collector_main.py
```

### 2. Avvia il Web API Server
```bash
python web_api_server.py
```

### 3. Avvia il Frontend
```bash
cd frontend
npm install
npm run dev
```

### 4. Avvia il Bridge (opzionale, per Arduino reale)
```bash
python bridge/bridge_Serial_MQTT.py
```

## 📊 Endpoint API Disponibili

- `GET /api/plants` - Tutte le piante
- `GET /api/plants/<id>` - Pianta specifica
- `GET /api/health` - Stato server
- `GET /api/stats` - Statistiche sistema

## 🧪 Test del Sistema

### Test API REST:
```bash
python test_web_api.py
```

### Test Data Collector:
```bash
python data_collector/data_collector_main.py
```

## 📁 Struttura Dati

I dati vengono salvati in `cloud_simulator/plants_log/` come file JSON:
- `plant_cactus_001.json` - Dati sensori e attuatori
- `my_cactus1.json` - Altri file di piante

## 🔧 Configurazione Policy

Le policy di irrigazione sono configurate in `data_collector/policies/policies_conf.json`:

```json
{
  "sensor": "humidity",
  "condition": "<",
  "value": 80,
  "actuator": "irrigation",
  "action": "activate"
}
```

## 🌐 Frontend Dashboard

Il frontend si connette automaticamente all'API su `http://localhost:5000/api` e:
- Mostra dati real-time dei sensori
- Visualizza stato irrigazione
- Aggiorna automaticamente ogni 10 secondi
- Supporta polling automatico

## 🔄 Flusso Dati

1. **Sensori** → Dati umidità via serial
2. **Bridge** → Converte e pubblica su MQTT
3. **Data Collector** → Riceve dati, salva JSON, applica policy
4. **Policy Manager** → Valuta regole e attiva/disattiva irrigazione
5. **Web API** → Legge JSON e espone via REST
6. **Frontend** → Polling API e visualizza dashboard

## 🎯 Soglie Irrigazione Attuali

- **Umidità < 80** → Attiva irrigazione
- **Umidità 80-120** → Zona neutra
- **Umidità > 120** → Disattiva irrigazione

## 🛠️ Troubleshooting

### Problemi Comuni:

1. **"ModuleNotFoundError"** → Verifica che tutti i moduli siano nel path
2. **"File non trovato"** → Assicurati che il data_collector sia in esecuzione
3. **"Connection refused"** → Verifica che il web server sia attivo su porta 5000
4. **"Nessun dato"** → Controlla che ci siano file JSON in `cloud_simulator/plants_log/`

### Log e Debug:

- Data Collector: Output console con emoji
- Web API: Log Flask su console
- Frontend: Console browser per errori API
