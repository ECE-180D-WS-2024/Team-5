#include <ArduinoBLE.h>
#include <Arduino_LSM6DS3.h>

#define BLE_UUID_ACCELEROMETER_SERVICE "1101"
#define BLE_UUID_MAX_ACC "2101"

#define BLE_DEVICE_NAME "Nano 33 IoT"
#define BLE_LOCAL_NAME "Nano 33 IoT"

BLEService accelerometerService(BLE_UUID_ACCELEROMETER_SERVICE);

BLEFloatCharacteristic maxAccCharacteristic(BLE_UUID_MAX_ACC, BLERead | BLENotify);

float ax, ay, az;

void setup() {
  Serial.begin(9600);
  while (!Serial);

  if (!IMU.begin()) {
    Serial.println("Failed to initialize IMU!");

    while (1);
  }

  Serial.print("Accelerometer sample rate = ");
  Serial.print(IMU.accelerationSampleRate());
  Serial.println(" Hz");
  Serial.println();
  Serial.println("Acceleration in g's");
  //Serial.println("ax\tY\tZ");

  // initialize BLE
  if (!BLE.begin()) {
    Serial.println("Starting Bluetooth® Low Energy module failed!");
    while (1)
      ;
  }
  
  // set advertised local name and service UUID
  BLE.setDeviceName(BLE_DEVICE_NAME);
  BLE.setLocalName(BLE_DEVICE_NAME);
  BLE.setAdvertisedService(accelerometerService);

  // add characteristics and service
  accelerometerService.addCharacteristic(maxAccCharacteristic);
  
  maxAccCharacteristic.writeValue(0);

  BLE.addService(accelerometerService);

  // start advertising
  BLE.advertise();

  Serial.println("BLE Accelerometer Peripheral");
}

void loop() {
  BLE.poll();
  BLEDevice central = BLE.central();

  // if a central is connected to peripheral:
  if (central) {
    float maxAcc = 0.0;
    float currentAcc = 0.0;

    Serial.print("Connected to central: ");
    // print the central's MAC address:
    Serial.println(central.address());

    // while the central is still connected to peripheral:
    while (central.connected()) {
      unsigned long startTime = millis();
      unsigned long sampleDuration = 1000;

      while(millis() - startTime < sampleDuration) {
        if (IMU.accelerationAvailable()) {
          IMU.readAcceleration(ax, ay, az);
          currentAcc = sqrt(ax*ax + ay*ay + az*az);

          if (currentAcc > maxAcc) {
            maxAcc = currentAcc;
            maxAccCharacteristic.writeValue(maxAcc);
          }
        }
      }
      if (maxAcc > 3.0) {
        Serial.println(maxAcc);
      }
    }
  }
}
