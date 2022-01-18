/*
 *  Create a WiFi AP and run a server returning DHT22 readings on it.
 *  
 *  requirements:
 *  - Additional board management URLs:
 *    - https://arduino.esp8266.com/stable/package_esp8266com_index.json
 *  - Boards:
 *    - ESP8266
 *  - Libs:
 *    - Adafruit DHT sensor library
*/

#include <DHT.h>
#include <ESP8266WiFi.h>
#include <WiFiClient.h>
#include <ESP8266WebServer.h>


/**
 * DHT22
 */
#define DHTPIN    2       // Digital pin connected to the DHT sensor
#define DHTTYPE   DHT22   // DHT 22 (AM2302)

DHT dht(DHTPIN, DHTTYPE);


/**
 * Server
 */
#ifndef AP_SSID
#define AP_SSID "ssid"
#define AP_SK   "password"
#endif

const char* ssid         = AP_SSID;
const char* password     = AP_SK;
const IPAddress ip_addr(192, 168, 4, 1);

ESP8266WebServer server(ip_addr, 80);

void handle_root() {
  float rh    = dht.readHumidity();     // Relative humidity (%)
  float temp  = dht.readTemperature();  // Temperature (Celsius)

  Serial.print(F("Server query\t"));
  Serial.print(F("Relative humidity: "));
  Serial.print(rh);
  Serial.print(F("%\t"));
  Serial.print(F("Temperature: "));
  Serial.print(temp);
  Serial.println(F("°C"));

  String text = "Relative humidity: ";
  text += rh;
  text += "%\nTemperature: ";
  text += temp;
  server.send(200, "text/plain", text);
}


/**
 * Execution
 */
void setup() {
  delay(1000);

  // DHT
  Serial.begin(115200);
  dht.begin();

  // Server
  WiFi.softAP(ssid, password);
  IPAddress ap_ip = WiFi.softAPIP();
  Serial.print("AP IP address: ");
  Serial.println(ap_ip);
  server.on("/", handle_root);
  server.begin();
  Serial.println("HTTP server started");
}

void loop() {
  server.handleClient();
}
