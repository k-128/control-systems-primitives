/**
 * Reads and print BMP388 readings.
 * 
 * Requirements:
 * - Libs:
 *   - BMP388_DEV by Martin Lindupp: github.com/MartinL1/BMP388_DEV
*/

#include <BMP388_DEV.h>


// Cfg
// ----------------------------------------------------------------------------
float temperature, pressure, altitude;
BMP388_DEV bmp388(4, 5); // SDA, SCL

const uint32_t delay_ms = 1000;   // Delay between measurements


// Exec
// ----------------------------------------------------------------------------
void setup()
{
  Serial.begin(115200);
  Serial.println();

  // NORMAL_MODE: performs continuous conversions separated by the standby time
  bmp388.begin(BMP388_I2C_ALT_ADDR);              // Sets BMP388 in SLEEP_MODE
  bmp388.setTimeStandby(TIME_STANDBY_1280MS);     // Set standby time
  bmp388.startNormalConversion();                 // Set NORMAL_MODE
}

void loop()
{
  if (bmp388.getMeasurements(temperature, pressure, altitude))
  {
    Serial.print(temperature);
    Serial.print(F("*C, "));
    Serial.print(pressure);
    Serial.print(F("hPa, "));
    Serial.print(altitude);
    Serial.println(F("m"));
  }

  delay(delay_ms);
}
