

#include <ArduinoBLE.h>
#include <Arduino_LSM9DS1.h> //Include the library for 9-axis IMU
#include <Arduino_LPS22HB.h> //Include library to read Pressure 
#include <Arduino_HTS221.h> //Include library to read Temperature and Humidity 
#include <Arduino_APDS9960.h> //Include library for colour, proximity and gesture recognition

const int ledPin1 = 22;
const int ledPin2 = 23;
const int ledPin3 = 24;


float accel_x, accel_y, accel_z;
float gyro_x, gyro_y, gyro_z;
float mag_x, mag_y, mag_z;
float pressure;
float temperature, humidity;
int proximity;
int Delay = 500;

// for BLE demo
int accelX=1;
int accelY=1;
float x, y, z;
BLEService customService("1101");
BLEUnsignedIntCharacteristic customXChar("2101", BLERead | BLENotify);
BLEUnsignedIntCharacteristic customYChar("2102", BLERead | BLENotify);
BLEUnsignedIntCharacteristic customZChar("2103", BLERead | BLENotify);
BLEUnsignedIntCharacteristic customTempChar("2104", BLERead | BLENotify);
BLEUnsignedIntCharacteristic customHumidityChar("2105", BLERead | BLENotify);
BLEUnsignedIntCharacteristic customPressChar("2106", BLERead | BLENotify);


void setup(){

  //pinMode(22, OUTPUT);
  //pinMode(23, OUTPUT);
  //pinMode(24, OUTPUT);
  
  Serial.begin(9600); //Serial monitor to display all sensor values 

  if (!IMU.begin()) //Initialize IMU sensor 
  { Serial.println("Failed to initialize IMU!"); while (1);}

  if (!BARO.begin()) //Initialize Pressure sensor 
  { Serial.println("Failed to initialize Pressure Sensor!"); while (1);}

  if (!HTS.begin()) //Initialize Temperature and Humidity sensor 
  { Serial.println("Failed to initialize Temperature and Humidity Sensor!"); while (1);}

  if (!APDS.begin()) //Initialize Colour, Proximity and Gesture sensor 
  { Serial.println("Failed to initialize Colour, Proximity and Gesture Sensor!"); while (1);}
 
  if (!BLE.begin()) {
    Serial.println("BLE failed to Initiate");
    delay(500);
    while (1);
  }
  
  BLE.setLocalName("Arduino Accelerometer");
  BLE.setAdvertisedService(customService);
  
  customService.addCharacteristic(customXChar);
  customService.addCharacteristic(customYChar);
  customService.addCharacteristic(customZChar);
  customService.addCharacteristic(customTempChar);
  customService.addCharacteristic(customHumidityChar);
  customService.addCharacteristic(customPressChar);
  
  BLE.addService(customService);
  customXChar.writeValue(accelX);
  customYChar.writeValue(accelY);
  
  BLE.advertise();
  
  Serial.println("Bluetooth device is now active, waiting for connections...");

  digitalWrite(LED_BUILTIN, LOW);

}

//BLE demo
void read_Accel() {

  if (IMU.accelerationAvailable())
  {
    IMU.readAcceleration(x, y, z);
    accelX = (1+x)*100;
    accelY = (1+y)*100;
  }
}

float Read_Temperature()
{
  return HTS.readTemperature();
}

float Read_Pressure()
{
 //Read Pressure value
  return BARO.readPressure();
}

float Read_Humidity()
{
  //Read Humidity value
  return HTS.readHumidity();
}

void  Magnetometer(int Delay)
{
  //Magnetometer values 
  if (IMU.magneticFieldAvailable()) {
    IMU.readMagneticField(mag_x, mag_y, mag_z);
    Serial.print("Magnetometer = ");Serial.print(mag_x); Serial.print(", ");Serial.print(mag_y);Serial.print(", ");Serial.println(mag_z);
  }
  delay (Delay);
}

void Accelerometer(int Delay)
{
  //Accelerometer values 
  if (IMU.accelerationAvailable()) {
    IMU.readAcceleration(accel_x, accel_y, accel_z);
    Serial.print("Accelerometer = ");Serial.print(accel_x); Serial.print(", ");Serial.print(accel_y);Serial.print(", ");Serial.println(accel_z);
  }
delay (Delay); 
}

void Gyroscope(int Delay)
{
  //Gyroscope values 
  if (IMU.gyroscopeAvailable()) {
    IMU.readGyroscope(gyro_x, gyro_y, gyro_z);
    Serial.print("Gyroscope = ");Serial.print(gyro_x); Serial.print(", ");Serial.print(gyro_y);Serial.print(", ");Serial.println(gyro_z);
  }
delay (Delay);
}

void Pressure(int Delay)
{
 //Read Pressure value
  pressure = BARO.readPressure();
  Serial.print("Pressure = ");Serial.println(pressure);
  delay (Delay);  
}

void Temperature(int Delay)
{
  //Read Temperature value
  temperature = HTS.readTemperature();
  Serial.print("Temperature: C(");Serial.print(temperature);
  Serial.print(") F(");Serial.print(9.0 / 5.0 * temperature + 32.0);
  Serial.println(")");
  delay (Delay);  
}

void Humidity(int Delay)
{
  //Read Humidity value
  humidity = HTS.readHumidity();
  Serial.print("Humidity = ");Serial.println(humidity);
  delay (Delay);  
}

void Proximity(int Delay)
{
  //Proximity value
  if (APDS.proximityAvailable()) {
    proximity = APDS.readProximity();
    Serial.print("Proximity = ");Serial.println(proximity); 
    }
  delay (Delay);  
}

void Gesture(int Delay)
{
  if (APDS.gestureAvailable()) {
    // a gesture was detected, read and print to serial monitor
    int gesture = APDS.readGesture();

    switch (gesture) {
      case GESTURE_UP:
        Serial.println("Detected UP gesture");
        digitalWrite(ledPin1, HIGH);
        digitalWrite(ledPin2, LOW);
        digitalWrite(ledPin3, LOW);
        //digitalWrite(ledPin1, LOW);
        delay(Delay);
        //digitalWrite(ledPin1, HIGH);
        break;

      case GESTURE_DOWN:
        Serial.println("Detected DOWN gesture");
        digitalWrite(ledPin1, LOW);
        digitalWrite(ledPin2, HIGH);
        digitalWrite(ledPin3, LOW);
        //digitalWrite(ledPin2, LOW);
         delay(Delay);
        //digitalWrite(ledPin2, HIGH);
        break;

      case GESTURE_LEFT:
        Serial.println("Detected LEFT gesture");
        digitalWrite(ledPin1, LOW);
        digitalWrite(ledPin2, LOW);
        digitalWrite(ledPin3, HIGH);
        //digitalWrite(ledPin3, LOW);
         delay(Delay);
        //digitalWrite(ledPin3, HIGH);
        break;

      case GESTURE_RIGHT:
        Serial.println("Detected RIGHT gesture");
        digitalWrite(ledPin1, HIGH);
        digitalWrite(ledPin2, HIGH);
        digitalWrite(ledPin3, LOW);
        //digitalWrite(LED_BUILTIN, HIGH);
        delay(Delay);
        //digitalWrite(LED_BUILTIN, LOW);
        break;

      default:
        // ignore
        break;
    }
  }
  else
  {
    //Serial.println("No Gester");
  }  
}

void loop()
{

  //Magnetometer(Delay);
  //Accelerometer(Delay);
  //Gyroscope(Delay);
  Pressure(Delay);
  Temperature(Delay);
  Humidity(Delay);
  //Proximity(Delay);
  
  //Gesture(Delay);
  //delay(20);

  BLEDevice central = BLE.central();
  if (central)
  {
    Serial.print("Connected to central: ");
    Serial.println(central.address());
    digitalWrite(LED_BUILTIN, HIGH);
    while (central.connected())
    {
      delay(200);
      read_Accel();
      
      customXChar.writeValue(accelX);
      //customYChar.writeValue(accelY);

      float fTemp = Read_Temperature();
      int iTemp = fTemp *100;
      customTempChar.writeValue(iTemp);

      float fHumidity = Read_Humidity();
      int iHumidity = fHumidity *100;
      customHumidityChar.writeValue(iHumidity);

      float fPress = Read_Pressure();
      int iPress = fPress *100;
      customPressChar.writeValue(iPress);      
    }
    digitalWrite(LED_BUILTIN, LOW);
  }
  
  //Serial.println("_____________________________________________________"); 
  //Accelerometer(Delay);
}
