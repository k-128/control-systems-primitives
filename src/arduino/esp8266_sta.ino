/**
 * Connects to a WiFi AP.
 * 
 * Requirements:
 * - Board: ESP8266
 * - Additional board management URLs:
 *   - https://arduino.esp8266.com/stable/package_esp8266com_index.json
*/

#include <ESP8266WiFi.h>


// Cfg
// ----------------------------------------------------------------------------
const char* ap_ssid     = "";
const char* ap_password = "";


// Exec
// ----------------------------------------------------------------------------
void setup()
{
  Serial.begin(115200);
  Serial.println();

  Serial.print("Connecting to Access Point...");
  WiFi.begin(ap_ssid, ap_password);
  while (WiFi.status() != WL_CONNECTED)
  {
    delay(500);
    Serial.print(".");
  }
  Serial.println();
  Serial.print("Connection to AP successful, IP address: ");
  Serial.println(WiFi.localIP());
}

void loop() {}
