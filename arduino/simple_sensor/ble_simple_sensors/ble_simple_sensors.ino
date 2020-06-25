

#include <ArduinoBLE.h>
#include <Arduino_LSM9DS1.h> //Include the library for 9-axis IMU
#include <Arduino_LPS22HB.h> //Include library to read Pressure 
#include <Arduino_HTS221.h> //Include library to read Temperature and Humidity 

int Delay = 1000;
int connectDelay = 200;

BLEService customService("1101");
BLEUnsignedIntCharacteristic customXChar("2101", BLERead | BLENotify);
//BLEUnsignedIntCharacteristic customYChar("2102", BLERead | BLENotify);
//BLEUnsignedIntCharacteristic customZChar("2103", BLERead | BLENotify);
BLEUnsignedIntCharacteristic customTempChar("2104", BLERead | BLENotify);
BLEUnsignedIntCharacteristic customHumidityChar("2105", BLERead | BLENotify);
BLEUnsignedIntCharacteristic customPressChar("2106", BLERead | BLENotify);


void setup()
{

  Serial.begin(9600); //Serial monitor to display all sensor values 

  if (!IMU.begin()) //Initialize IMU sensor 
  { Serial.println("Failed to initialize IMU!"); while (1);}

  if (!BARO.begin()) //Initialize Pressure sensor 
  { Serial.println("Failed to initialize Pressure Sensor!"); while (1);}

  if (!HTS.begin()) //Initialize Temperature and Humidity sensor 
  { Serial.println("Failed to initialize Temperature and Humidity Sensor!"); while (1);}

  if (!BLE.begin()) {
    Serial.println("BLE failed to Initiate");
    delay(500);
    while (1);
  }
  
  BLE.setLocalName("Arduino Accelerometer");
  BLE.setAdvertisedService(customService);
  
  customService.addCharacteristic(customXChar);
  //customService.addCharacteristic(customYChar);
  //customService.addCharacteristic(customZChar);
  customService.addCharacteristic(customTempChar);
  customService.addCharacteristic(customHumidityChar);
  customService.addCharacteristic(customPressChar);
  
  BLE.addService(customService);
  customXChar.writeValue(1);
  //customYChar.writeValue(1);
  //customZChar.writeValue(1);
  
  BLE.advertise();
  
  Serial.println("Bluetooth device is now active, waiting for connections...");

  digitalWrite(LED_BUILTIN, LOW);

}

void BLE_Update_Accel()
{
  float x,y,z;
  
  if (IMU.accelerationAvailable())
  {
    IMU.readAcceleration(x, y, z);

    customXChar.writeValue((1+x)*1000);
    //customYChar.writeValue((1+y)*1000);
    //customZChar.writeValue((1+z)*1000);
  }
}

void BLE_Update_Temperature()
{
  float fTemp = HTS.readTemperature();
  int iTemp = fTemp * 100;
  customTempChar.writeValue(iTemp);
}

void BLE_Update_Pressure()
{
  float fPress = BARO.readPressure();
  int iPress = fPress * 100;
  customPressChar.writeValue(iPress);      
}

void BLE_Update_Humidity()
{
  float fHumidity = HTS.readHumidity();
  int iHumidity = fHumidity * 100;
  customHumidityChar.writeValue(iHumidity);
}

void loop()
{

  BLEDevice central = BLE.central();
  if (central)
  {
    Serial.print("Connected to central: ");
    Serial.println(central.address());
    digitalWrite(LED_BUILTIN, HIGH);
    while (central.connected())
    {
        BLE_Update_Accel();
        BLE_Update_Temperature();
        BLE_Update_Humidity();
        BLE_Update_Pressure();
        delay(Delay);
   }
    digitalWrite(LED_BUILTIN, LOW);
  } 
    delay(connectDelay);
}
