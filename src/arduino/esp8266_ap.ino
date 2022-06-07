/**
 * Create a WiFi AP and run a server returning random values.
 * 
 * Requirements:
 * - Board: ESP8266
 * - Additional board management URLs:
 *   - https://arduino.esp8266.com/stable/package_esp8266com_index.json
 * 
 * Resources:
 * - https://arduino-esp8266.readthedocs.io/en/latest/esp8266wifi/readme.html
 * - https://github.com/esp8266/Arduino/tree/master/libraries/ESP8266WebServer
*/

#include <ESP8266WiFi.h>
#include <ESP8266WebServer.h>


// Cfg
// ----------------------------------------------------------------------------
const char* ap_ssid       = "";
const char* ap_password   = "";
const uint8_t ap_channel  = 11;
const bool ap_hidden      = false;
const uint8_t ap_max_conn = 4;  // Max STA on AP - 0 to 8, Default: 4
const IPAddress ap_ip_addr(192, 168, 6, 1);
const IPAddress ap_gateway(192, 168, 6, 1);
const IPAddress ap_subnet_mask(255, 255, 255, 0);

ESP8266WebServer server(80);


// Server
// ----------------------------------------------------------------------------
void handle_root()
{
  const long v = random(300);
  String json_string = "{\"v\":";
  json_string += v;
  json_string += "}";

  Serial.print(F("Recv. query, sending value: "));
  Serial.println(json_string);
  server.send(200, "application/json", json_string);
}


// Exec
// ----------------------------------------------------------------------------
void setup()
{
  Serial.begin(115200);
  Serial.println();

  // Access Point
  Serial.println("Creating Access Point...");
  WiFi.persistent(false);
  WiFi.mode(WIFI_AP);
  WiFi.softAPConfig(ap_ip_addr, ap_gateway, ap_subnet_mask);
  WiFi.softAP(ap_ssid, ap_password, ap_channel, ap_hidden, ap_max_conn);
  IPAddress ap_ip = WiFi.softAPIP();
  Serial.print("AP created, IP address: ");
  Serial.println(ap_ip);

  // Server
  Serial.println("Setting server...");
  server.on("/", handle_root);
  server.begin();
  Serial.println("HTTP server started");
}

void loop()
{
  server.handleClient();
}
