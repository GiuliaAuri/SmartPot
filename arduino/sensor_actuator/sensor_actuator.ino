const int SENSORPIN = A0;
unsigned long timestamp;
const int RELAY_PIN=7;

void setup() {

  Serial.begin(9600);
  timestamp = millis();
  pinMode(RELAY_PIN,OUTPUT);
  digitalWrite(RELAY_PIN, HIGH); // relè spento all'avvio (low-level trigger)
  
}

void loop() {
  int val;
  if (millis() - timestamp > 2000){
    // sensore
    val = analogRead(SENSORPIN);

    // pacchetto dati
    // FF  1 dato  FE
    Serial.write(0xFF);
    Serial.write(1);
    
    Serial.write(map(val,0,1023,0,253));

    Serial.write(0xFE);

    // attuatore
    if (Serial.available()>1)
    { int val;
      val = Serial.read();
      if (val=='A') digitalWrite(RELAY_PIN, HIGH); //acceso
      if (val=='S') digitalWrite(RELAY_PIN, LOW); //spento
      
    }
    
    timestamp = millis();

    
  }
  
}