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

I dati raccolti vengono **pubblicati** sul topic MQTT con la seguente struttura: 

 plant/{plant_id}/device/{device_id}/telemetry/{resource_id}

## 💧 Attuatore per l’Irrigazione

L’attuatore che gestisce l’irrigazione non pubblica dati, ma è **sottoscritto** a un topic dedicato ai comandi:

plant/{plant_id}/device/{device_id}/command/{resource_id}



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


