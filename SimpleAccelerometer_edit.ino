#include <ArduinoBLE.h>
#include <Arduino_LSM6DS3.h>

#define BLE_UUID_ACCELEROMETER_SERVICE "1101"
#define BLE_UUID_ACCELEROMETER_X "2101"

#define BLE_DEVICE_NAME "Nano 33 IoT"
#define BLE_LOCAL_NAME "Nano 33 IoT"

BLEService accelerometerService(BLE_UUID_ACCELEROMETER_SERVICE);

BLEFloatCharacteristic accelerometerCharacteristicX(BLE_UUID_ACCELEROMETER_X, BLERead | BLENotify);

float ax, ay, az;

void setup() {
  Serial.begin(9600);
  while (!Serial)
    ;

  // initialize IMU
  if (!IMU.begin()) {
    Serial.println("Failed to initialize IMU!");
    while (1)
      ;
  }

  Serial.print("Accelerometer sample rate = ");
  Serial.print(IMU.accelerationSampleRate());
  Serial.println("Hz");

  // initialize BLE
  if (!BLE.begin()) {
    Serial.println("Starting Bluetooth® Low Energy module failed!");
    while (1)
      ;
  }

  // set advertised local name and service UUID
  //
  BLE.setDeviceName(BLE_DEVICE_NAME);
  BLE.setLocalName(BLE_DEVICE_NAME);
  BLE.setAdvertisedService(accelerometerService);

  // add characteristics and service
  //
  accelerometerService.addCharacteristic(accelerometerCharacteristicX);
  
  accelerometerCharacteristicX.writeValue(0);

  BLE.addService(accelerometerService);

  // start advertising
  //
  BLE.advertise();

  Serial.println("BLE Accelerometer Peripheral");
}

void loop() {
  BLE.poll();
  BLEDevice central = BLE.central();

  // obtain and write accelerometer data
  // 

  // if a central is connected to peripheral:
  if (central) {
    float maxAcc = 0.0;
    float currentAcc = 0.0;
    Serial.print("Connected to central: ");
    // print the central's MAC address:
    Serial.println(central.address());

    // while the central is still connected to peripheral:
    while (central.connected()) {
      if (IMU.accelerationAvailable()) {
        IMU.readAcceleration(ax, ay, az);
        currentAcc = sqrt(ax*ax + ay*ay + az*az);
        Serial.println(ax);
        if (currentAcc > 6.5) {
          accelerometerCharacteristicX.writeValue(currentAcc);
        }
      }
    }

    // when the central disconnects, print it out:
    Serial.print(F("Disconnected from central: "));
    Serial.println(central.address());
  }
}