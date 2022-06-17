/**
 * Scans i2c bus for connected devices.
*/

#include <Wire.h>


const uint32_t delay_ms = 2000; // Delay between scans

void scan_i2c()
{
  Serial.println(F("Running i2c scan..."));

  bool is_dev_found         = false;
  const uint8_t nb_of_addr  = 127;

  for (int i = 1; i < nb_of_addr; ++i )
  {
    Wire.beginTransmission(i);
    uint8_t error = Wire.endTransmission();

    if (error == 0)
    {
      Serial.print("I2C device found at address 0x");
      if (i < 16)
      {
        Serial.print(F("0"));
      }
      Serial.println(i, HEX);
      is_dev_found = true;
    }
    else if (error == 4)
    {
      Serial.print(F("Error at address 0x"));
      if (i < 16)
      {
        Serial.print(F("0"));
      }
      Serial.println(i, HEX);
    }
  }

  if (!is_dev_found)
  {
    Serial.println(F("No I2C devices found"));
  }
  Serial.println();
}

void setup()
{
  Serial.begin(115200);
  Serial.println();
  Wire.begin();
}

void loop()
{
  scan_i2c();
  delay(delay_ms);
}
