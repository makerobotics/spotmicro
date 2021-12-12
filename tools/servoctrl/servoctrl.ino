#include <Arduino.h>
#include <RotaryEncoder.h>
#include <Wire.h>
#include <Adafruit_PWMServoDriver.h>
#include <ESP32Servo.h>//#include <Servo.h>
#include <EEPROM.h>
#include "BluetoothSerial.h"

#define BUILTINLED 2
#define PIN_IN1 16
#define PIN_IN2 17
#define PIN_IN3 26 // button
#define SERVO_PIN 19
#define MAX_PRESSED 20
#define LONG_PRESS  1500000
#define VERY_LONG_PRESS  10000000
#define BTN_UNPRESSED 0
#define BTN_PRESSED   1
#define BTN_DEBOUNCE  2
#define STEP          1 // function is called twice per rotary actuation
#define MAX_SERVO_NUM 12
#define EEPROM_SIZE MAX_SERVO_NUM*4

#define PCA9685   0
#if PCA9685
  #define SERVOMIN  50
  #define SERVOMAX  900
#else
  #define SERVOMIN  500
  #define SERVOMAX  2500
#endif
// Setup a RotaryEncoder with 4 steps per latch for the 2 signal input pins:
// RotaryEncoder encoder(PIN_IN1, PIN_IN2, RotaryEncoder::LatchMode::FOUR3);

// Setup a RotaryEncoder with 2 steps per latch for the 2 signal input pins:
RotaryEncoder encoder(PIN_IN1, PIN_IN2, RotaryEncoder::LatchMode::TWO03);
#if PCA9685
  Adafruit_PWMServoDriver pwm1 = Adafruit_PWMServoDriver(0x40);
#else
  Servo myservo;  // create servo object to control a servo
#endif
BluetoothSerial SerialBT;

int clicked = 0;
int servoPos[MAX_SERVO_NUM] = {SERVOMIN};
int servoPosMin[MAX_SERVO_NUM] = {SERVOMIN};
int servoPosMax[MAX_SERVO_NUM] = {SERVOMAX};
int servonum = 0;

void log(char * text, int value){
  Serial.print(text);
  Serial.println(value);
  SerialBT.print(text);
  SerialBT.println(value);
}

void readEEPROM(){
  int eeAddress = 0;
  for(int i=0;i<MAX_SERVO_NUM;i++){
    EEPROM.get(eeAddress, servoPosMin[i]);
    /*Serial.print("Adr: ");
    Serial.print(eeAddress);
    Serial.print(", Val: ");
    Serial.println(servoPosMin[i]);*/
    eeAddress += sizeof(int);
    EEPROM.get(eeAddress, servoPosMax[i]);
    /*Serial.print("Adr: ");
    Serial.print(eeAddress);
    Serial.print(", Val: ");
    Serial.println(servoPosMax[i]);*/
    eeAddress += sizeof(int);
  }
}

void initializeEEPROM(){
  int eeAddress = 0;
  for(int i=0;i<MAX_SERVO_NUM;i++){
    EEPROM.put(eeAddress, SERVOMIN);
    eeAddress += sizeof(int);
    delay(100);
    EEPROM.put(eeAddress, SERVOMAX);
    eeAddress += sizeof(int);
    delay(100);
  }
  EEPROM.commit();
}

void writeBoundary(int servonumber, int servoPosition){
  if(servoPosition > ((SERVOMAX-SERVOMIN)/2)){
    EEPROM.put(servonumber*sizeof(int)*2+sizeof(int), servoPosition);
    log("Write servo position: ", servoPosition);
    log("On servo number: ", servonumber);
    log("At adress: ", servonumber * sizeof(int) * 2 + sizeof(int));
  }
  else {
    EEPROM.put(servonumber*sizeof(int)*2, servoPosition);
    log("Write servo position: ", servoPosition);
    log("On servo number: ", servonumber);
    log("At adress: ", servonumber * sizeof(int) * 2);
  }
  delay(100);
  EEPROM.commit();
}

void resetBoundary(int servonumber){
  EEPROM.put(servonumber*sizeof(int)*2+sizeof(int), SERVOMAX);
  delay(100);
  EEPROM.put(servonumber*sizeof(int)*2, SERVOMIN);
  delay(100);
  EEPROM.commit();
}

int handlePushButton(){
  int ret = 0;
  int btn = digitalRead(PIN_IN3);
  static int pressed = 0;
  static int event_pressed = 0;
  static int longPress = 0;
  
  if(btn == 0){
    if(pressed < MAX_PRESSED) {
      pressed++;
      event_pressed = BTN_DEBOUNCE;
    }
    else {
      event_pressed = BTN_PRESSED;
      longPress++;
      // Indicate long and very long press by led
      if(longPress == LONG_PRESS) digitalWrite(BUILTINLED, HIGH);
      if(longPress == VERY_LONG_PRESS) digitalWrite(BUILTINLED, LOW);
    
      if (clicked == 0) clicked = 1;
    }
  }
  else{
    if(pressed > 0) {
      pressed--;
      event_pressed = BTN_DEBOUNCE;
    }
    else {
      event_pressed = BTN_UNPRESSED;
      if(clicked == 1) clicked = 2;
    }
  }
  if(clicked == 2){
    //Serial.println("button clicked");
    ret = 1;
    if(longPress >= VERY_LONG_PRESS) ret = 3;
    else if(longPress >= LONG_PRESS) ret = 2;
    longPress = 0;
    clicked = 0; // to reset the event. Could also be moved outside...
  }
  return ret;
}

void setup()
{
  Serial.begin(115200);
  while (! Serial);
  pinMode(PIN_IN3, INPUT_PULLUP);
  pinMode(BUILTINLED, OUTPUT);
  
  SerialBT.begin("servotest"); // bluetooth device name
  
  //Init EEPROM
  EEPROM.begin(EEPROM_SIZE);
  readEEPROM();

  log("Started", 0);
#if PCA9685
  pwm1.begin();
  pwm1.setPWMFreq(60);  // This is the maximum PWM frequency
#else
  myservo.attach(SERVO_PIN, SERVOMIN, SERVOMAX);  // attaches the servo (redefine ranges s they were changed in ESP8266 V3.0.0)
  servoPos[servonum] = (SERVOMAX+SERVOMIN)/2;
  myservo.writeMicroseconds((SERVOMAX+SERVOMIN)/2);
#endif

} // setup()


// Read the current position of the encoder and print out when changed.
void loop()
{
  static int pos = 0;

  encoder.tick();
  int newPos = encoder.getPosition();

  if (pos != newPos) {
    /*Serial.print("pos:");
    Serial.print(newPos);
    Serial.print(" dir:");
    Serial.println((int)(encoder.getDirection()));*/
    
    pos = newPos;
    
    servoPos[servonum] += STEP * (int)(encoder.getDirection()) * (-1); // Inverse button increment
    if(servoPos[servonum] < servoPosMin[servonum]) servoPos[servonum] = servoPosMin[servonum];
    if(servoPos[servonum] > servoPosMax[servonum]) servoPos[servonum] = servoPosMax[servonum];

    log(" Servo position: ", servoPos[servonum]);
  #if PCA9685
    pwm1.setPWM(servonum, 0, servoPos[servonum]);   
  #endif
    myservo.writeMicroseconds(servoPos[servonum]);
  } // if

  int btnEvent = handlePushButton();
  if (btnEvent == 1) {
    //Serial.println("Clicked");
    log(" Servo number: ", servonum);
    //initializeEEPROM();
    readEEPROM();
  }
  else if(btnEvent == 2){
    log(" Long press", 0);
    digitalWrite(BUILTINLED, HIGH);
    writeBoundary(servonum, servoPos[servonum]);
    delay(1500);
    digitalWrite(BUILTINLED, LOW);
    readEEPROM();
  }
  else if(btnEvent == 3){
    log("Very long press", 0);
    digitalWrite(BUILTINLED, HIGH);
    resetBoundary(servonum);
    delay(3000);
    digitalWrite(BUILTINLED, LOW);
    readEEPROM();
  }
} // loop ()

// The End