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
                  Add warning light if hard reset is required
                  Verify ArrayFull Functionality
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
#define WEARABLE_STR_CHAR_UUID128 "45-98-FB-6C-F5-6B-40-28-AD-27-E3-F7-AA-14-89-1F"
#define PACKET_LENGTH 10   // Define the length of a packet (in bytes)   
#define PACKET_ARRAY_LENGTH 50  // Define in multiples of 5                       

Adafruit_BNO055 bno = Adafruit_BNO055(55);

/********************************************************************/
float heading = 0;
int quad = 0; // break 360 degree heading into 4 quadrants
String imuData; // Map FP compass heading & step count
boolean quadChange = false; // track if the quadrant # has changed -> concat step count to string

// Step Count (Pedometer Variables)
int tiltSwitch = 3; // Tilt Switch Input
int tiltVal = 0; // variable to store tilt input
int tiltOldVal; // tilt last state
int stepCount = 0; // state change iterator

  String empID = "001"; // track employee ID    
  String buffPacket;
  int oldQuad;  //track state change
  int count = 0; // placeholder to iterate through packetBuilder
  int packetNumber = 0;   // So the gateway can place packet in correct order within the file

  // STRTX() variables
  int transmit;          // In order to ensure proper packet data exists within IMU data string
  int maxTransmit = 5;
  boolean arrayEmpty = false;
  boolean transmitSuccess = false;

/* The BLE service information */
int32_t wearServiceId;
int32_t wearStringCharId;
boolean success;
//char buff[PACKET_LENGTH];        // Used to iterate through IMU data and place in <UUID><PacketNum><quad><setCount> sequence
String packetBuilder;
String packetData[PACKET_ARRAY_LENGTH]; // Store IMU data into packets-> iterate through array to send over BLE

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
  oldQuad = quad;
  count = 0;
  packetBuilder = empID;
  packetBuilder += "|";
  tiltOldVal = tiltVal;

  if (0 < heading && heading < 90) {
    quad = 1;
  } else if (91 < heading && heading < 180) {
    quad = 2;
  } else if (181 < heading && heading < 270) {
    quad = 3;
  } else if (271 < heading && heading < 360) {
    quad = 4;
  } 

  tiltVal = digitalRead (tiltSwitch) ;// read the switch value
        
  if (tiltVal != tiltOldVal) //Step State changed
  {
    stepCount++;
  }
  
  if (oldQuad != quad) {  //Quadrant state change -> new course detected!
    imuData += oldQuad;
    imuData += "|";
    imuData += stepCount;
    imuData += "|";
    stepCount = 0;

    //build BLE Packet
    Serial.print("Packet Number: ");
    Serial.println(packetNumber);
    packetBuilder += packetNumber;
    packetBuilder += "|";
    packetBuilder += imuData;

    Serial.print("imuData length: ");
    Serial.println(imuData.length());
    // parse through packetbuilder to place in packet array data
    while (imuData.length()>0){
      
      //.getBytes(buff,PACKET_LENGTH)
      String str = packetBuilder.substring(0,PACKET_LENGTH);
      packetData[packetNumber] = str;
//      Serial.print("Str: ");
//      Serial.println(str);
//
//    for(int i = 0; i<packetNumber; i++){
//         Serial.print("Packet Array: ");
//         Serial.println(packetData[i]);
//      }  
     
      // delete last packet
      packetBuilder = packetBuilder.substring(PACKET_LENGTH);

      // iterate for next packet 
      imuData = imuData.substring(PACKET_LENGTH);
      packetNumber+=1;
      if (packetNumber>PACKET_ARRAY_LENGTH+2){
        fullPacketArray();
      }
      count += PACKET_LENGTH;
    }
  }

    //set BLE packet to array
//    packetData[packetNumber] = buffPacket;

  // Serial.print("Quadrant: \t");
  //Serial.println(imuData);
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

//void StrTX(){
//  delay(1000);
// // memset(buff,0,sizeof(buff));    //initialize buffer to 0
//  
////  if (count<str.length()){
////    //str.substring(count,count+PACKET_LENGTH).getBytes(buff,PACKET_LENGTH);
////    Serial.print("Buffer: ");
////    Serial.println(buff);
////    Serial.print("string: ");
////    Serial.println(str);
////
////    setCharacteristic(wearTXCharId, buff);
////    
////  }
//
//    Serial.print("transmit: ");
//    Serial.print(transmit);
//    Serial.print("\tmaxTransmit: ");
//    Serial.println(maxTransmit);
//        Serial.print("\tpacketData: ");
//        Serial.println(packetData[transmit]);
//
//    if (packetData[transmit].length()==0){   //end of data in array
//      Serial.println("empty ARRAY");
//      transmit = 0;
//      maxTransmit = 5;
//      arrayEmpty = true;
//      }
//      
//    if (maxTransmit >= PACKET_ARRAY_LENGTH) {
//      Serial.println("FULL ARRAY");
//      transmit = 0;
//      maxTransmit = 5;
//      int halfArray = floor(0.5*PACKET_ARRAY_LENGTH);
//      int j = halfArray;
//      for (int i = 0; i<halfArray; i++) {
//        packetData[i]=packetData[j];
//        packetData[j]= "";
//        j++;
//      }
//    }  
//    
//    int localCounter = transmit;  
//    while ((localCounter < maxTransmit) && (!arrayEmpty)) {
//          setCharacteristic(wearStringCharId, packetData[localCounter]);
//          localCounter++;
//    }
//    Serial.println("Increment");
//    transmit= transmit+ 5;
//    Serial.println("Increment 2");
//    maxTransmit=maxTransmit+5;
//    arrayEmpty = false;
//    
//    
//}

void StrTX(){
  int localCount=transmit;

  if(packetData[transmit].length() == 0  || packetData[transmit+1].length() == 0 || packetData[transmit+2].length() == 0
                                           || packetData[transmit+3].length() == 0 || packetData[transmit+4].length() == 0){
      arrayEmpty = true;
      transmit=0;
      maxTransmit=5;
      
    }
    
  while((maxTransmit<PACKET_ARRAY_LENGTH) && (!arrayEmpty) && localCount < maxTransmit) {
    Serial.print("localCount: ");
    Serial.println(localCount);
    setCharacteristic(wearStringCharId, packetData[localCount]);
    localCount++;
    transmitSuccess = true;
  }

  if (transmitSuccess) {
    transmit+=5;
    maxTransmit+=5;
  }

  if (maxTransmit >= PACKET_ARRAY_LENGTH+5) {
      fullPacketArray();
  }
  arrayEmpty = false;
  transmitSuccess = false;
  Serial.print("transmit: ");
  Serial.print(transmit);
  Serial.print("\tmaxTransmit: ");
  Serial.println(maxTransmit);
}
void fullPacketArray(){
//    Serial.println("FULL ARRAY");
//    int a = 0;
//    for (a=0; a < PACKET_ARRAY_LENGTH; a++) {
//      Serial.println(" ARRAY BEFORE");
//      Serial.print(a);
//      Serial.print(": ");
//      Serial.println(packetData[a]);
//    }
    transmit = 0;
    maxTransmit = 5;
    int halfArray = floor(0.5*PACKET_ARRAY_LENGTH);
    int j = halfArray;
    for (int i = 0; i<halfArray; i++) {
      packetData[i]=packetData[j];
      packetData[j]= "";
      j++;
    }

//    int b = 0;
//    for (b=0; b < PACKET_ARRAY_LENGTH; b++) {
//      Serial.println(" ARRAY AFTER");
//      Serial.print(b);
//      Serial.print(": ");
//      Serial.println(packetData[b]);
//    }
}
void setCharacteristic(int32_t charId, String str){
  ble.print(F("AT+GATTCHAR="));
  ble.print(charId,DEC);
  ble.print(F(","));
  ble.println(str);
  if (!ble.waitForOK()){
    Serial.println(F("Failed to get a response"));
  }

 // str = empID + "|";
  
}

/********************************************************************/
void setup() {
  Serial.begin(9600);
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
  Serial.println(F("Setting device name to 'wearable': "));

  if (! ble.sendCommandCheckOK(F("AT+GAPDEVNAME=Wearable")) ) {
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
  StrTX();

 
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
