/*
   Connections - BNO055
   ===========
   Connect SCL to analog 5
   Connect SDA to analog 4
   Connect VDD to 3.3V DC
   Connect GROUND to common ground

   Connections - KY-017 - tilt switch
   ===========
   +----------+
   |          |
   |          | - S - D3
   |          | - Power (5v)
   |          | - G - ground
   |          |
   +----------+

   History
   =======
   02/25/19  - V 1.0
   03/21/19  - V 1.5
        Changes:  Added tilt switch
                          Accelorometer from IMU had calibration issues
                  Added quadrant tracking
                  Added pedometer functionality
                  Added string builder (what gets sent over BLE

    03/22/19 - V 1.6
        Changes:  Added BLE Services
                  TODO: Test Services on PI
                  
        TODO:     Add junk calibration validation (if calibration = 0 dont accept data)
*/

#include <Wire.h>
#include <Adafruit_Sensor.h>
#include <Adafruit_BNO055.h>
#include <utility/imumaths.h>

#include "Adafruit_BLE.h"
#include "Adafruit_BluefruitLE_SPI.h"
#include "Adafruit_BluefruitLE_UART.h"

#include "BluefruitConfig.h"

#if SOFTWARE_SERIAL_AVAILABLE
  #include <SoftwareSerial.h>
#endif

#define BNO055_SAMPLERATE_DELAY_MS (500)
// FROM ONLINE GUID GENERATOR -> define GUIDs for BLE service & characteristic
#define WEARABLE_SERVICE_UUID128  "d9-bd-9b-0e-da-5e-42-de-90-cf-54-5c-7d-17-19-12"
#define WEARABLE_STR_CHAR_UUID128 "23-36-30-e5-0f-b6-45-ba-82-1c-c8-a0-c1-a2-21-fe"

Adafruit_BNO055 bno = Adafruit_BNO055(55);

/********************************************************************/
float heading = 0;
int quad = 0; // break 360 degree heading into 8 quadrants
String empID = "001"; // track employee ID
String str = empID + " | "; // Map FP compass heading & step count
boolean quadChange = false; // track if the quadrant # has changed -> concat step count to string

// Step Count (Pedometer Variables)
int tiltSwitch = 3; // Tilt Switch Input
int tiltVal = 0; // variable to store tilt input
int tiltOldVal = 0; // tilt last state
int stepCount = 0; // state change iterator


/* The BLE service information */
int32_t wearServiceId;
int32_t wearStringCharId;

SoftwareSerial bluefruitSS = SoftwareSerial(BLUEFRUIT_SWUART_TXD_PIN, BLUEFRUIT_SWUART_RXD_PIN);

Adafruit_BluefruitLE_UART ble(bluefruitSS, BLUEFRUIT_UART_MODE_PIN,
                      BLUEFRUIT_UART_CTS_PIN, BLUEFRUIT_UART_RTS_PIN);

void error(const __FlashStringHelper*err) {
  Serial.println(err);
  while (1);
}

/********************************************************************/

void ReadHeading() { // Output: HEADING
  imu::Vector<3> euler = bno.getVector(Adafruit_BNO055::VECTOR_EULER);
  heading = (float)euler.x();
  heading -= 90; // Adjust for true north

  if (heading < 0 ) {
    heading = 360 + heading;
  }

  if (heading > 360) {
    heading = heading - 360;
  }
  //Serial.print("Heading: \t");
  //Serial.println(heading);
}

void quadrantBuilder() {
  int oldQuad = quad;  //track state change

  if (0 < heading && heading < 45) {
    quad = 1;
  } else if (44 < heading && heading < 90) {
    quad = 2;
  } else if (89 < heading && heading < 135) {
    quad = 3;
  } else if (134 < heading && heading < 180) {
    quad = 4;
  } else if (179 < heading && heading < 225) {
    quad = 5;
  } else if (224 < heading && heading < 270) {
    quad = 6;
  } else if (269 < heading && heading < 315) {
    quad = 7;
  } else if (314 < heading && heading < 360) {
    quad = 8;
  }

  tiltVal = digitalRead (tiltSwitch) ;// read the switch value

  if (tiltVal != tiltOldVal) //Step State changed
  {
    stepCount++;
    //    Serial.print("Step Count = ");
    //    Serial.println(stepCount);
  }
  

  if (oldQuad != quad) {  //Quadrant state change -> new course detected!
    str += oldQuad;
    str += " | ";
    str += stepCount;
    str += " | ";
    stepCount = 0;
    
  }

  // Serial.print("Quadrant: \t");
  //Serial.println(str);
}

void imuStatus() {
  /* check calibration data for each sensor. */
  uint8_t system, gyro, accel, mag;
  system = gyro = accel = mag = 0;
  bno.getCalibration(&system, &gyro, &accel, &mag);
  Serial.print(F("Calibration: "));
  Serial.print(system, DEC);
  Serial.print(F(" "));
  Serial.print(gyro, DEC);
  Serial.print(F(" "));
  Serial.print(accel, DEC);
  Serial.print(F(" "));
  Serial.println(mag, DEC);
}

void setCharacteristic(int32_t charId, String str){
  ble.print(F("AT+GATTCHAR="));
  ble.print(charId,DEC);
  ble.print(F(","));
  ble.println(str);
  if (!ble.waitForOK()){
    Serial.println(F("Failed to get a response"));
  } else {
    // sent string & reset
    str = empID + " | ";
  }
  
}

/********************************************************************/
void setup() {
  Serial.begin(115200);
  if (!bno.begin())
  {
    /* There was a problem detecting the BNO055 ... check your connections */
    Serial.print("Ooops, no BNO055 detected ... Check your wiring or I2C ADDR!");
    while (1);
  }
  //  imuStatus();
  pinMode (tiltSwitch, INPUT) ;// define the mercury tilt switch sensor output interface

  if ( !ble.begin(VERBOSE_MODE) )
  {
    error(F("Couldn't find Bluefruit, make sure it's in CoMmanD mode & check wiring?"));
  }
  Serial.println( F("OK!") );
   /* Perform a factory reset to make sure everything is in a known state */
  Serial.println(F("Performing a factory reset: "));
  if (! ble.factoryReset() ){
       error(F("Couldn't factory reset"));
  }

  /* Disable command echo from Bluefruit */
  ble.echo(false);

  Serial.println("Requesting Bluefruit info:");
  /* Print Bluefruit information */
  ble.info();

  // this line is particularly required for Flora, but is a good idea
  // anyways for the super long lines ahead!
   ble.setInterCharWriteDelay(5); // 5 ms

  /* Change the device name to make it easier to find */
  Serial.println(F("Setting device name to 'Wear Test': "));

  if (! ble.sendCommandCheckOK(F("AT+GAPDEVNAME=Wear Test")) ) {
    error(F("Could not set device name?"));
  }

  /* Add the Wearable Service definition */
  /* Service ID should be 1 */
  Serial.println(F("Adding the Wearable Service definition (UUID = 0x180D): "));
  success = ble.sendCommandWithIntReply( F("AT+GATTADDSERVICE=UUID128=" WEARABLE_SERVICE_UUID128 ), &wearServiceId);
  if (! success) {
    error(F("Could not add Wearable service"));
  }

  /* Add the Wearable String characteristic */
  /* Chars ID for Measurement should be 1 */
  Serial.println(F("Adding the Wearable String characteristic: "));
  success = ble.sendCommandWithIntReply( F("AT+GATTADDCHAR=UUID128=" WEARABLE_STR_CHAR_UUID128 ", PROPERTIES=0x12, MIN_LEN=1, MAX_LEN=20"), &wearStringCharId);
    if (! success) {
    error(F("Could not add Wearable String characteristic"));
  }

  /* Reset the device for the new service setting changes to take effect */
  Serial.print(F("Performing a SW reset (service changes require a reset): "));
  ble.reset();
}

/********************************************************************/

void loop() {

  imuStatus();
  ReadHeading();
  quadrantBuilder();

  setCharacteristic(wearStringCharId, str);
 // Serial.println(str);


  // imu::Vector<3> euler = bno.getVector(Adafruit_BNO055::VECTOR_MAGNETOMETER);

  // test point
  /* Display the floating point data */
  //  Serial.print("X: ");
  //  Serial.print(euler.x());
  //  Serial.print(" Y: ");
  //  Serial.print(euler.y());
  //  Serial.print(" Z: ");
  //  Serial.println(euler.z());


  delay(BNO055_SAMPLERATE_DELAY_MS);
}
