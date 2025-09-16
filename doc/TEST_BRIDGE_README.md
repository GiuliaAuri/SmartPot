# 🧪 Test Bridge Serial MQTT - Arduino

## Descrizione
Questi test verificano il funzionamento completo del sistema bridge tra Arduino e MQTT, testando sia i sensori che gli attuatori.

## File di Test

### 1. `test_bridge_arduino_complete.py` - Test Completo
**Test completo con mock e simulazione Arduino**

**Caratteristiche:**
- ✅ Test di inizializzazione del bridge
- ✅ Test elaborazione dati sensori (mock)
- ✅ Test elaborazione comandi attuatori (mock)
- ✅ Test comandi MQTT reali
- ✅ Simulazione Arduino per test live

**Come usare:**
```bash
python test_bridge_arduino_complete.py
```

**Opzioni:**
- `1` - Test completo (mock)
- `2` - Test live con Arduino simulato
- `3` - Entrambi

### 2. `test_bridge_quick.py` - Test Rapido
**Test rapido per verificare il funzionamento in tempo reale**

**Caratteristiche:**
- ✅ Monitoraggio messaggi MQTT in tempo reale
- ✅ Test comandi attuatori
- ✅ Monitoraggio dati sensori
- ✅ Interfaccia semplice e intuitiva

**Come usare:**
```bash
python test_bridge_quick.py
```

## Prerequisiti

### 1. Broker MQTT
Assicurati che il broker MQTT sia attivo:
```bash
# Avvia il broker Docker
cd mqtt_broker
docker-compose up -d

# Oppure usa Mosquitto direttamente
mosquitto -p 7883
```

### 2. Bridge Attivo
Avvia il bridge prima di eseguire i test:
```bash
python bridge/bridge_Serial_MQTT.py
```

### 3. Arduino (Opzionale)
- Collega Arduino alla porta seriale configurata
- Carica il codice `arduino/sensor_actuator/sensor_actuator.ino`
- Verifica la porta in `bridge/config.ini`

## Cosa Testano i Test

### 📊 Test Sensori
- **Ricezione dati seriale** da Arduino
- **Parsing protocollo** (FF + num_valori + valori + FE)
- **Pubblicazione MQTT** sui topic corretti:
  - `plant/sensor/humidity`
  - `plant/sensor/temperature`
  - `plant/sensor/lightness`
  - `plant/sensor/battery_level`

### 🎮 Test Attuatori
- **Ricezione comandi MQTT** dal broker
- **Parsing comandi** (start/on/1 vs stop/off/0)
- **Invio comandi seriali** ad Arduino:
  - `I` + `A` per ATTIVA
  - `I` + `S` per DISATTIVA

### 🌐 Test MQTT
- **Connessione broker** MQTT
- **Sottoscrizione topic** comandi
- **Pubblicazione topic** sensori
- **Gestione errori** di connessione

## Esempi di Output

### Test Sensori
```
📡 Arduino invia: ['0xff', '0x4', '0x41', '0x2d', '0x1e', '0x55', '0xfe']
📊 Valori sensori: humidity=65, temperature=45, lightness=30, battery=85
📡 MQTT pubblicato - Topic: plant/sensor/humidity, Payload: 65
📡 MQTT pubblicato - Topic: plant/sensor/temperature, Payload: 45
```

### Test Attuatori
```
📨 Comando ricevuto - Topic: plant/test/device/irrigation/command, Payload: b'start'
📤 Comando seriale inviato: b'I'
📤 Comando seriale inviato: b'A'
✅ Comando ATTIVA inviato
```

## Risoluzione Problemi

### ❌ "Serial port not available!"
- Verifica che Arduino sia collegato
- Controlla la porta in `bridge/config.ini`
- Verifica che la porta non sia usata da altri programmi

### ❌ "Errore connessione MQTT"
- Verifica che il broker MQTT sia attivo
- Controlla host e porta in `bridge/config.ini`
- Verifica la configurazione di rete

### ❌ "Comando non riconosciuto"
- Usa solo comandi supportati: start/on/1 o stop/off/0
- Verifica che il payload sia una stringa di testo

### ⚠️ "Nessun messaggio ricevuto"
- Verifica che il bridge sia attivo
- Controlla che Arduino stia inviando dati
- Verifica la configurazione dei topic MQTT

## Configurazione Avanzata

### Modificare Mapping Sensori
Nel file `bridge/bridge_Serial_MQTT.py`:
```python
SENSOR_MAPPING = {
    0: "humidity", 
    1: "temperature",
    2: "lightness", 
    3: "battery_level"
}
```

### Modificare Mapping Attuatori
```python
ACTUATOR_MAPPING = {
    0: "irrigation",
    1: "lighting",
    2: "fan"
}
```

### Aggiungere Nuovi Comandi
Nel metodo `on_message()`:
```python
elif command == "pulse":
    self.ser.write(b'I')
    self.ser.write(b'P')  # Nuovo comando
    print("Comando PULSE inviato")
```

## Supporto

Per problemi o domande:
1. Controlla i log del bridge
2. Verifica la configurazione MQTT
3. Testa la connessione seriale
4. Consulta la documentazione del sistema

