
const int dir = 6;  // 
const int en = 7;  // 
const int step = 4;  // 

int sensorPin = A0; // the potentiometer is connected to analog pin 0
int sensorValue; // an integer variable to store the potentiometer reading
int incomingByte;       // a variable to read incoming serial data into

void setup() {
  // initialize serial communication:
  Serial.begin(115200);
  // initialize the pin as an output:
  pinMode(dir, OUTPUT);
  // initialize the pin as an output:
  pinMode(en, OUTPUT);
  // initialize the pin as an output:
  pinMode(step, OUTPUT);
  //start with disabled motor
  digitalWrite(en, HIGH);//+5V means disabled with DM556T driver
}

void loop() { // this loop runs repeatedly after setup() finishes
  if (Serial.available() > 0) { // see if there's incoming serial data
    // read the oldest byte in the serial buffer:
    incomingByte = Serial.read();
    // if it's a capital F (forward), give signal on respective pin:
    if (incomingByte == 'F') {
      digitalWrite(dir, HIGH);
    }
    // if it's a capital B (backward), give signal on respective pin:
    if (incomingByte == 'B') {
      digitalWrite(dir, LOW);
    }
    // if it's a capital E (enabled), give signal on respective pin:
    if (incomingByte == 'E') {
      digitalWrite(en, LOW);
    }
    // if it's a capital D (disabled), give signal on respective pin:
    if (incomingByte == 'D') {
      digitalWrite(en, HIGH);
    }    
    // if it's a capital S (step), give signal on respective pin:
    if (incomingByte == 'S') {
      digitalWrite(step, HIGH);
    }
    // if it's a capital H (hold), give signal on respective pin:
    if (incomingByte == 'H') {
      digitalWrite(step, LOW);
    }
   
    sensorValue = analogRead(sensorPin); // read the sensor
    Serial.println(sensorValue, DEC); // output reading to the serial line
    //delay (100); // Pause in milliseconds before next reading
  }
}

