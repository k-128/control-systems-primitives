/**
 * Reads and print TDS CQR values from an ADS1X15.
 * 
 * Requirements:
 * - Libs:
 *   - Adafruit ADS1X15 by Adafruit: github.com/adafruit/Adafruit_ADS1X15
*/

#include <Adafruit_ADS1X15.h>


// Cfg
// ----------------------------------------------------------------------------
Adafruit_ADS1115 ads; // (Adafruit_ADS1015|Adafruit_ADS1115)
const uint8_t ads_tds_idx = 0;

const uint32_t loop_ms = 1000;
unsigned long prev_ms  = 0;


// Exec
// ----------------------------------------------------------------------------
float get_tds_cqr_value(const float temperature = 25.0)
{
  const float compens_coef = 0.02 * (temperature - 25.0) + 1.0;
  const int16_t adc = ads.readADC_SingleEnded(ads_tds_idx);
  const float v     = ads.computeVolts(adc) / compens_coef;
  const float tds = (133.42 * pow(v, 3) - 255.86 * pow(v, 2) + 857.39 * v) / 2;
  Serial.print(F("ADC"));
  Serial.print(ads_tds_idx);
  Serial.print(F(": "));
  Serial.print(adc);
  Serial.print(F("; "));
  Serial.print(v);
  Serial.print(F("V; "));
  Serial.print(tds);
  Serial.println(F("ppm"));
  return tds;
}

void setup()
{
  Serial.begin(115200);
  Serial.println();

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
    get_tds_cqr_value();
  }
}
