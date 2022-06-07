/**
 * Create a WiFi AP and run a server returning DHT readings.
 * 
 * Requirements:
 * - Board: ESP8266
 * - Additional board management URLs:
 *   - https://arduino.esp8266.com/stable/package_esp8266com_index.json
 * - Libs:
 *   - DHT sensor library by Adafruit: github.com/adafruit/DHT-sensor-library
 *   - ArduinoJson by Benoit Blanchon: github.com/bblanchon/ArduinoJson
 * 
 * Resources:
 * - https://arduino-esp8266.readthedocs.io/en/latest/esp8266wifi/readme.html
 * - https://github.com/esp8266/Arduino/tree/master/libraries/ESP8266WebServer
*/

#include <DHT.h>
#include <ESP8266WiFi.h>
#include <ESP8266WebServer.h>
#include <ArduinoJson.h>


// Cfg
// ----------------------------------------------------------------------------
const uint8_t dht_pin   = D5;     // i: GPIO or Di, ex: D4 (common onboard LED)
const uint8_t dht_type  = DHT22;  // DHT.h: DHT11, DHT12, DHT21, DHT22, AM2301
DHT sen_dht(dht_pin, dht_type);

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
void handle_text()
{
  float rh    = sen_dht.readHumidity();     // Relative humidity (%)
  float temp  = sen_dht.readTemperature();  // Temperature (Celsius)

  Serial.print(F("Recv. query text, sending DHT data:\t"));
  Serial.print(F("temp: "));
  Serial.print(temp);
  Serial.print(F("°C, rh: "));
  Serial.print(rh);
  Serial.println(F("%"));
  String text = "Temperature: ";
  text += rh;
  text += "°C\tRelative humidity: ";
  text += temp;
  text += "%";
  server.send(200, "text/plain", text);
}

void handle_json()
{
  float rh    = sen_dht.readHumidity();     // Relative humidity (%)
  float temp  = sen_dht.readTemperature();  // Temperature (Celsius)

  String json_string = "{\"temp\":";
  json_string += temp;
  json_string += ",\"rh\":";
  json_string += rh;
  json_string += "}";
  Serial.print(F("Recv. query json, sending DHT data:\t"));
  Serial.println(json_string);
  server.send(200, "application/json", json_string);
}

void handle_json_2()
{
  float rh    = sen_dht.readHumidity();     // Relative humidity (%)
  float temp  = sen_dht.readTemperature();  // Temperature (Celsius)

  const int capacity = JSON_OBJECT_SIZE(2);
  StaticJsonDocument<capacity> doc;
  doc["rh"]   = rh;
  doc["temp"] = temp;
  String json_string;
  serializeJson(doc, json_string);
  Serial.print(F("Recv. query json2, sending DHT data:\t"));
  Serial.println(json_string);
  server.send(200, "application/json", json_string);
}


// Exec
// ----------------------------------------------------------------------------
void setup()
{
  delay(1000);
  Serial.begin(115200);
  Serial.println();

  // Sensor
  sen_dht.begin();

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
  server.on("/", handle_json);
  server.on("/json/", handle_json);
  server.on("/json2/", handle_json_2);
  server.on("/text/", handle_text);
  server.begin();
  Serial.println("HTTP server started");
}

void loop()
{
  server.handleClient();
}
