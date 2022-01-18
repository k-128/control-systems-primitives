/*
 *  Reads and print DHT22 measurements.
 *  
 *  requirements:
 *  - Libs:
 *    - Adafruit DHT sensor library
*/

#include <DHT.h>


#define DHTPIN    2       // Digital pin connected to the DHT sensor
#define DHTTYPE   DHT22   // DHT 22 (AM2302)

DHT dht(DHTPIN, DHTTYPE);

uint32_t delay_ms = 1000; // Delay between measurements

void setup() {
  Serial.begin(115200);
  dht.begin();
}

void loop() {
  float rh    = dht.readHumidity();     // Relative humidity (%)
  float temp  = dht.readTemperature();  // Temperature (Celsius)

  Serial.print(F("Relative humidity: "));
  Serial.print(rh);
  Serial.print(F("%\t"));
  Serial.print(F("Temperature: "));
  Serial.print(temp);
  Serial.println(F("°C"));

  delay(delay_ms);
}
