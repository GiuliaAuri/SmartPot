#include "Arduino_LED_Matrix.h"
ArduinoLEDMatrix matrix;

// --- LED Matrix ---
const uint32_t smile[8] = {
  0x19819,
  0x80004024,
  0x27fe000,
  0x0,
  0x0,
  0x0,
  0x0,
  0x0
};

const uint32_t animation_drop[][8] = {
  {0x400a011, 0x1100e00, 0x0, 66, 0, 0, 0, 0},
  {0x400a,    0x1101100, 0xe0000000, 66, 0, 0, 0, 0},
  {0x4,       0xa01101, 0x100e0000, 66, 0, 0, 0, 0},
  {0x0,       0x400a01, 0x101100e0, 66, 0, 0, 0, 0}
};
const int NUM_FRAMES = sizeof(animation_drop) / sizeof(animation_drop[0]);


const int SENSOR_PIN = A0;
const char SENSOR_TYPE = 'H';
unsigned long timestamp;
const int RELAY_PIN=7;
const char ACTUATOR_TYPE = 'I';

void setup() {

  Serial.begin(9600);
  timestamp = millis();
  pinMode(RELAY_PIN,OUTPUT);
  digitalWrite(RELAY_PIN, HIGH); // relè spento all'avvio (low-level trigger)

  // LED Matrix
  matrix.begin();
  matrix.loadFrame(smile);
  
}

void loop() {
  int val;
  if (millis() - timestamp > 2000){
    // sensore
    val = analogRead(SENSOR_PIN);

    // pacchetto dati
    // FF  numero type dato  FE
    Serial.write(0xFF);
    Serial.write(1);
    Serial.write(SENSOR_TYPE);
    
    Serial.write(map(val,0,1023,0,253));

    Serial.write(0xFE);

    // attuatore
    if (Serial.available()>0)
    { int val;
      char type;
      type = Serial.read();
      val = Serial.read();
      if (type==ACTUATOR_TYPE) {
        if (val=='A') digitalWrite(RELAY_PIN, LOW); //acceso
        if (val=='S') digitalWrite(RELAY_PIN, HIGH); //spento
      }
    }
    
    timestamp = millis();

  }
  // --- Gestione LED Matrix ---
  if (digitalRead(RELAY_PIN) == LOW) {
    // relè acceso -> animation drop
    for (int i = 0; i < NUM_FRAMES; i++) {
      matrix.loadFrame(animation_drop[i]);
      delay(200); // velocità animazione
    }
  } else {
    // relè spento -> smile
    matrix.loadFrame(smile);
  }
}
