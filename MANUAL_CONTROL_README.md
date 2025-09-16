# 🌱 Plants System - Controllo Manuale Irrigazione

## **✅ SISTEMA COMPLETO IMPLEMENTATO**

Hai ragione! Per attivare l'irrigazione dal frontend, ho implementato:

1. **Endpoint POST** nel backend
2. **Backend scrive** il nuovo stato nel file JSON
3. **Backend invia** comando MQTT all'attuatore

## **🔗 ENDPOINT POST DISPONIBILI**

### **Controllo Attuatore Generico**
```http
POST /api/plants/{plant_id}/actuators/{actuator_type}
Content-Type: application/json

{
  "action": "start" | "stop" | "activate" | "deactivate" | "on" | "off"
}
```

**Esempi:**
```bash
# Controlla irrigazione
curl -X POST http://localhost:5000/api/plants/plant_cactus_001/actuators/irrigation \
  -H "Content-Type: application/json" \
  -d '{"action": "start"}'

# Controlla illuminazione (esempio futuro)
curl -X POST http://localhost:5000/api/plants/plant_cactus_001/actuators/lighting \
  -H "Content-Type: application/json" \
  -d '{"action": "activate"}'
```

## **🔄 FLUSSO COMPLETO**

1. **Frontend** → Clicca pulsante "Start" o "Stop"
2. **API Call** → POST `/api/plants/{id}/actuators/irrigation`
3. **Backend** → Valida azione e converte in comando semplice
4. **Backend** → Salva azione nel file JSON
5. **Backend** → Invia comando MQTT all'attuatore
6. **Bridge** → Riceve comando MQTT e invia a Arduino
7. **Arduino** → Attiva/disattiva irrigatore fisico

## **📊 RISPOSTA API**

```json
{
  "success": true,
  "message": "Irrigazione start per plant_cactus_001",
  "plant_id": "plant_cactus_001",
  "action": "start",
  "mqtt_sent": true,
  "timestamp": "2025-09-16T12:15:30.123456Z"
}
```

## **💾 SALVATAGGIO DATI**

Le azioni vengono salvate nel file JSON:
```json
{
  "actuators": {
    "irrigation": [
      {
        "action": "start",
        "timestamp": 1758018242
      },
      {
        "action": "stop", 
        "timestamp": 1758018300
      }
    ]
  }
}
```

## **🎯 FRONTEND AGGIORNATO**

Il frontend ora include:
- **Pulsanti Start/Stop** per controllo manuale
- **API Service** con metodi `controlIrrigation()`
- **Aggiornamento automatico** dopo ogni azione
- **Stato sincronizzato** con il backend

## **🧪 TEST**

```bash
# Test endpoint POST
python test_post_endpoints.py

# Test backend diretto
python -c "
from backend.web_api_server import PlantDataService
service = PlantDataService('cloud_simulator/plants_log')
service._save_actuator_action('plant_cactus_001', 'irrigation', 'start')
"
```

## **🚀 AVVIO SISTEMA**

```bash
# 1. Backend API Server
python backend/web_api_server.py

# 2. Frontend
cd frontend
npm run dev

# 3. Data Collector (opzionale)
python data_collector/data_collector_main.py
```

**Il sistema è completamente funzionale per il controllo manuale dell'irrigazione dal frontend!** 🎉
