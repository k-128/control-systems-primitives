/**
 * Reads and print DS18B20 readings.
 * 
 * Requirements:
 * - Libs:
 *   - OneWire by Paul Stoffregen: github.com/PaulStoffregen/OneWire
 *   - DallasTemperature by Miles Burton: github.com/milesburton/Arduino-Temperature-Control-Library
*/

#include <OneWire.h>
#include <DallasTemperature.h>


// Cfg
// ----------------------------------------------------------------------------
const uint8_t one_wire_bus = D3;  // i: GPIO or Di, ex: D4 (common onboard LED)
OneWire oneWire(one_wire_bus);
DallasTemperature sen_ds18b20(&oneWire);

const uint32_t delay_ms = 1000;   // Delay between measurements


// Exec
// ----------------------------------------------------------------------------
void setup()
{
  Serial.begin(115200);
  Serial.println();
  sen_ds18b20.begin();
}

void loop()
{
  sen_ds18b20.requestTemperatures();

  // getTempCByIndex (slow, see .h), (idx: n OneWire sensors)
  const float temp = sen_ds18b20.getTempCByIndex(0);

  String json_string = "{\"temp\":";
  json_string += temp;
  json_string += "}";
  Serial.println(json_string);

  delay(delay_ms);
}
