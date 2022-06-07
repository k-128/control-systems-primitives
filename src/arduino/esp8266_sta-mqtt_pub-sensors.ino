/**
 * Connect to a WiFi AP running a MQTT broker and publish sensors readings to it
 * 
 * Requirements:
 * - Board: ESP8266
 * - Additional board management URLs:
 *   - https://arduino.esp8266.com/stable/package_esp8266com_index.json
 * - Libs:
 *   - Adafruit ADS1X15 by Adafruit: github.com/adafruit/Adafruit_ADS1X15
 *   - OneWire by Paul Stoffregen: github.com/PaulStoffregen/OneWire
 *   - DallasTemperature by Miles Burton: github.com/milesburton/Arduino-Temperature-Control-Library
 *   - DHT sensor library by Adafruit: github.com/adafruit/DHT-sensor-library
 *   - ArduinoMqttClient by Arduino: github.com/arduino-libraries/ArduinoMqttClient
*/

#include <Adafruit_ADS1X15.h>
#include <OneWire.h>
#include <DallasTemperature.h>
#include <DHT.h>
#include <ESP8266WiFi.h>
#include <ArduinoMqttClient.h>


// Cfg
// ----------------------------------------------------------------------------
Adafruit_ADS1115 ads; // (Adafruit_ADS1015|Adafruit_ADS1115)
const uint8_t ads_tds_idx = 0;

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
float get_tds_cqr_value(const float temperature = 25.0)
{
  const float compens_coef = 0.02 * (temperature - 25.0) + 1.0;
  const int16_t adc = ads.readADC_SingleEnded(ads_tds_idx);
  const float v = ads.computeVolts(adc) / compens_coef;
  const float tds = (133.42 * pow(v, 3) - 255.86 * pow(v, 2) + 857.39 * v) / 2;
  return tds;
}

void publish_data()
{
  sen_ds18b20.requestTemperatures();
  const float temp_hydr = sen_ds18b20.getTempCByIndex(0);
  const float rh        = sen_dht.readHumidity();     // Relative humidity (%)
  const float temp      = sen_dht.readTemperature();  // Temperature (Celsius)
  const float tds       = get_tds_cqr_value(temp_hydr);

  String json_string = "{\"temp_hydr\":";
  json_string += temp_hydr;
  json_string += ",\"temp\":";
  json_string += temp;
  json_string += ",\"rh\":";
  json_string += rh;
  json_string += ",\"tds\":";
  json_string += tds;
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
  Serial.println();

  // Sensors
  ads.setGain(GAIN_TWOTHIRDS);  // (dflt) +-6.144 V
  if (!ads.begin())
  {
    Serial.println("Failed to initialize ADS.");
    while (1);
  }
  sen_ds18b20.begin();
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
