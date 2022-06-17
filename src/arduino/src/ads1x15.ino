/**
 * Reads and print values from an ADS1X15.
 * 
 * Requirements:
 * - Libs:
 *   - Adafruit ADS1X15 by Adafruit: github.com/adafruit/Adafruit_ADS1X15
*/

#include <Adafruit_ADS1X15.h>


// Cfg
// ----------------------------------------------------------------------------
Adafruit_ADS1115 ads; // (Adafruit_ADS1015|Adafruit_ADS1115)

const uint32_t loop_ms = 1000;
unsigned long prev_ms  = 0;


// Exec
// ----------------------------------------------------------------------------
void read_potentiometer_value(
  const uint8_t ads_idx,
  const float max_voltage = 3.3)
{
  const int16_t adc = ads.readADC_SingleEnded(ads_idx);
  const float v     = ads.computeVolts(adc);
  const float pct   = v / max_voltage * 100;
  Serial.print(F("(potentiometer) ADC"));
  Serial.print(ads_idx);
  Serial.print(F(": "));
  Serial.print(adc);
  Serial.print(F("; "));
  Serial.print(v);
  Serial.print(F("V; "));
  Serial.print(pct);
  Serial.println(F("%"));
}

void read_ads_values()
{
  for (size_t i = 0; i < 4; ++i)
  {
    const int16_t adc = ads.readADC_SingleEnded(i);
    const float v     = ads.computeVolts(adc);
    Serial.print(F("ADC"));
    Serial.print(i);
    Serial.print(F(": "));
    Serial.print(adc);
    Serial.print(F("; "));
    Serial.print(v);
    Serial.println(F("V"));
  }
  Serial.println(F(""));
}

void setup()
{
  Serial.begin(115200);
  println();

  ads.setGain(GAIN_TWOTHIRDS);  // (dflt) +-6.144 V
  if (!ads.begin())
  {
    Serial.println("Failed to initialize ADS.");
    while (1);
  }
}

void loop()
{
  unsigned long curr_ms = millis();
  if (curr_ms - prev_ms >= loop_ms)
  {
    prev_ms = curr_ms;
    read_potentiometer_value(1);
    read_ads_values();
  }
}
