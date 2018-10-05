
//Set Up Sonar Sensor
#include "SR04.h"
#define TRIG_PIN 6
#define ECHO_PIN 5
SR04 sr04 = SR04(ECHO_PIN, TRIG_PIN);


//Set Up Motor Controller
int data;

float distance = 1;
float adjustment = 1;

boolean newCommand = false;
float ms_per_cm_up = 750;
float ms_per_cm_down = 890;

int CHECK_CONTROLLER_PIN = 13;
int UP_PIN = 12;
int DOWN_PIN = 11;
int controllerOff = 1;

static byte nowReadingDistance = 0;
static byte ndx = 0;
static char endMarker = '\n';
static char splitMarker = ' ';


char rc;
int numChars = 10;
char receivedDirection[10]; // an array to store the received data
char receivedDistance[10];

void setup() {
  Serial.begin(9600); //initialize serial COM at 9600 baudrate
  pinMode(LED_BUILTIN, OUTPUT); //make the LED pin (13) as output
  digitalWrite (LED_BUILTIN, LOW);
  
  pinMode(CHECK_CONTROLLER_PIN, INPUT);
  pinMode(UP_PIN, OUTPUT);
  pinMode(DOWN_PIN, OUTPUT);
  digitalWrite(UP_PIN, HIGH);
  digitalWrite(DOWN_PIN, HIGH);
  controllerOff = digitalRead(CHECK_CONTROLLER_PIN);
}

void loop() {
  
  if (Serial.available() && newCommand == false){
    static byte nowReadingDistance = 0;
    static byte ndx = 0;
    char endMarker = '\n';
    char splitMarker = ' ';
    char rc;
    
    rc = Serial.read();

  
    if (rc == splitMarker) {
        receivedDirection[ndx] = '\0';
        nowReadingDistance = 1;
        ndx = 0;
        }
    else if (rc == endMarker){
      nowReadingDistance = 0;
      receivedDistance[ndx] = '\0'; // terminate the string
      ndx = 0;
      newCommand = true;
      runCommand();
      }
    else {
        if (nowReadingDistance == 1) {
          receivedDistance[ndx] = rc;
          ndx++;
          if (ndx >= numChars) {
            ndx = numChars - 1;
          }
        }
        else {
          receivedDirection[ndx] = rc;
          ndx++;
          if (ndx >= numChars) {
            ndx = numChars - 1;
          }
        }
        
      }
  }
  else{
    //long sonar_distance = sr04.Distance();
    //Serial.print(sonar_distance);  
    //Serial.println("mm");  
    //delay(1000);
  }
}

void runCommand() {
    digitalWrite(UP_PIN, HIGH);
  digitalWrite(DOWN_PIN, HIGH);
  controllerOff = digitalRead(CHECK_CONTROLLER_PIN);
  
  if (newCommand == true) {
    if (!controllerOff){
      float distance = atof(receivedDistance);
      if (receivedDirection[0] == 'u') {
        Serial.print("Going up ");
        Serial.print(distance);
        Serial.println(" cm");
        if (distance > 0.5){
          adjustment = 1.115;
          }
        digitalWrite(UP_PIN, LOW);
        delay(distance*adjustment*ms_per_cm_up);
        digitalWrite(UP_PIN, HIGH);
      }
      
      else if (receivedDirection[0] == 'd'){
        Serial.print("Going down ");
        Serial.print(distance);
        Serial.println(" cm");
        
        digitalWrite(DOWN_PIN, LOW);
        delay(distance*adjustment*ms_per_cm_down);  
        digitalWrite(DOWN_PIN, HIGH);
      }
      
      else{
        Serial.print(receivedDirection);
        Serial.println("Command not understood");  
      }
    newCommand = false;
    } 
  }
}
