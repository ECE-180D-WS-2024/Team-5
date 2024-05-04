#include <Arduino_LSM6DS3.h>

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
  //Serial.println("X\tY\tZ");
}

void loop() {
  float x, y, z;
  float maxAcc = 0.0;
  float currentAcc = 0.0;

  unsigned long startTime = millis();
  unsigned long sampleDuration = 1000;

  while(millis() - startTime < sampleDuration) {
    if (IMU.accelerationAvailable()) {
      IMU.readAcceleration(x, y, z);
      currentAcc = sqrt(x*x + y*y + z*z);

      if (currentAcc > maxAcc) {
        maxAcc = currentAcc;
      }
    }
  }
  if (maxAcc > 3.0) {
    Serial.println(maxAcc);
  }
}
