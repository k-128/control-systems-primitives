/**
 * Connect to a WiFi AP running a MQTT broker and publish sensors readings to it
 * 
 * Requirements:
 * - Board: ESP8266
 * - Additional board management URLs:
 *   - https://arduino.esp8266.com/stable/package_esp8266com_index.json
 * - Libs:
 *   - DHT sensor library by Adafruit: github.com/adafruit/DHT-sensor-library
 *   - OneWire by Paul Stoffregen: github.com/PaulStoffregen/OneWire
 *   - DallasTemperature by Miles Burton: github.com/milesburton/Arduino-Temperature-Control-Library
 *   - ArduinoMqttClient by Arduino: github.com/arduino-libraries/ArduinoMqttClient
*/

#include <OneWire.h>
#include <DallasTemperature.h>
#include <DHT.h>
#include <ESP8266WiFi.h>
#include <ArduinoMqttClient.h>


// Cfg
// ----------------------------------------------------------------------------
const uint8_t one_wire_bus = D3;  // i: GPIO or Di, ex: D4 (common onboard LED)
OneWire oneWire(one_wire_bus);
DallasTemperature sen_ds18b20(&oneWire);

const uint8_t dht_pin   = D5;     // i: GPIO or Di, ex: D4 (common onboard LED)
const uint8_t dht_type  = DHT22;  // DHT.h: DHT11, DHT12, DHT21, DHT22, AM2301
DHT sen_dht(dht_pin, dht_type);

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
  sen_ds18b20.requestTemperatures();
  float temp_hydr = sen_ds18b20.getTempCByIndex(0);
  float rh        = sen_dht.readHumidity();     // Relative humidity (%)
  float temp      = sen_dht.readTemperature();  // Temperature (Celsius)

  String json_string = "{\"temp_hydr\":";
  json_string += temp_hydr;
  json_string += ",\"temp\":";
  json_string += temp;
  json_string += ",\"rh\":";
  json_string += rh;
  json_string += "}";

  Serial.print(F("Publishing sensors data [topic: "));
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
  while (!Serial);
  Serial.println();

  // Sensor
  sen_dht.begin();

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
