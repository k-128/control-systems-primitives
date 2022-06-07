/**
 * Connect to a WiFi AP running a MQTT broker and publish random values.
 * 
 * Requirements:
 * - Board: ESP8266
 * - Additional board management URLs:
 *   - https://arduino.esp8266.com/stable/package_esp8266com_index.json
 * - Libs:
 *   - ArduinoMqttClient by Arduino: github.com/arduino-libraries/ArduinoMqttClient
*/

#include <ESP8266WiFi.h>
#include <ArduinoMqttClient.h>


// Cfg
// ----------------------------------------------------------------------------
const char* ap_ssid     = "";
const char* ap_password = "";

WiFiClient wifiClient;
MqttClient mqttClient(wifiClient);
const char* broker        = "";
const uint32_t port       = 1883;
const char* client_id     = "";
const char* mqtt_user     = "";
const char* mqtt_password = "";
const char* topic         = "";

const uint32_t loop_ms = 2000;
unsigned long prev_ms  = 0;


// Exec
// ----------------------------------------------------------------------------
void publish_data()
{
  const long v = random(300);
  String json_string = "{\"v\":";
  json_string += v;
  json_string += "}";

  Serial.print(F("Publishing value [topic: "));
  Serial.print(topic);
  Serial.print(F("] - "));
  Serial.println(json_string);

  mqttClient.beginMessage(topic);
  mqttClient.print(json_string);
  mqttClient.endMessage();
}

void setup()
{
  Serial.begin(115200);
  Serial.println();

  // Value
  randomSeed(analogRead(0));

  // Server
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

  Serial.print("Connecting to MQTT Broker... ");
  Serial.println(broker);
  mqttClient.setId(client_id);
  mqttClient.setUsernamePassword(mqtt_user, mqtt_password);

  if (!mqttClient.connect(broker, port))
  {
    Serial.print("MQTT connection failed. Error code: ");
    Serial.println(mqttClient.connectError());
    while (1);
  }

  Serial.println("Connection to MQTT Broker successful.");
  Serial.println();
}

void loop()
{
  unsigned long curr_ms = millis();
  if (curr_ms - prev_ms >= loop_ms)
  {
    prev_ms = curr_ms;
    publish_data();
  }
}
