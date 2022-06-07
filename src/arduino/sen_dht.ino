/**
 * Reads and print DHT readings.
 * 
 * Requirements:
 * - Libs:
 *   - DHT sensor library by Adafruit: github.com/adafruit/DHT-sensor-library
*/

#include <DHT.h>


// Cfg
// ----------------------------------------------------------------------------
const uint8_t dht_pin   = D5;     // i: GPIO or Di, ex: D4 (common onboard LED)
const uint8_t dht_type  = DHT22;  // DHT.h: DHT11, DHT12, DHT21, DHT22, AM2301
DHT sen_dht(dht_pin, dht_type);

const uint32_t delay_ms = 1000;   // Delay between measurements


// Exec
// ----------------------------------------------------------------------------
void setup()
{
  Serial.begin(115200);
  sen_dht.begin();
}

void loop()
{
  float rh    = sen_dht.readHumidity();     // Relative humidity (%)
  float temp  = sen_dht.readTemperature();  // Temperature (Celsius)

  String json_string = "{\"temp\":";
  json_string += temp;
  json_string += ",\"rh\":";
  json_string += rh;
  json_string += "}";
  Serial.println(json_string);

  delay(delay_ms);
}
