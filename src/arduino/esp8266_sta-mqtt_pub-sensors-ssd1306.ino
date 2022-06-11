/**
 * Funcs:
 * - Display sensors readings on a SSD1306
 * - Optionally connect to a WiFi AP and MQTT broker and publish readings to it
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
 *   - BMP388_DEV by Martin Lindupp: github.com/MartinL1/BMP388_DEV
 *   - Adafruit SSD1306 by Adafruit; github.com/adafruit/Adafruit_SSD1306
 *   - ArduinoMqttClient by Arduino: github.com/arduino-libraries/ArduinoMqttClient
*/

#include <Wire.h>
#include <Adafruit_SSD1306.h>
#include <Adafruit_ADS1X15.h>
#include <OneWire.h>
#include <DallasTemperature.h>
#include <DHT.h>
#include <BMP388_DEV.h>
#include <ESP8266WiFi.h>
#include <ArduinoMqttClient.h>


// Cfg
// ----------------------------------------------------------------------------
// Sensors
const float   kSenErrorValue = -273.15;

Adafruit_ADS1115 ads;  // Adafruit_ADS1X15.h: Adafruit_ADS1015|Adafruit_ADS1115
const uint8_t kAdsTdsIdx  = 0;
const uint8_t kAdsPhIdx   = 1;
const uint8_t kOneWireBus = D3;     // i: GPIO or Di, ex: D4 (common board LED)
const uint8_t kDhtPin     = D5;
const uint8_t kDhtType    = DHT22;  // DHT.h: DHT11|DHT12|DHT21|DHT22|AM2301
const uint8_t kCtcWtrPin  = D6;

// Display
const uint8_t kDisplayWidth     = 128;
const uint8_t kDisplayHeight    = 64;
const int8_t  kDisplayOledReset = -1;
const uint8_t kDisplayAddress   = 0x3C;  // (0x3C|0x3D)

// Server
const char*   kApSsid       = "";
const char*   kApPassword   = "";
const char*   kMqttHost     = "";
const uint    kMqttPort     = 1883;
const char*   kMqttClientID = "";
const char*   kMqttUser     = "";
const char*   kMqttPassword = "";
const char*   kMqttTopic    = "";

// Exec
const uint8_t  kPinLedInputOpMode   = D4;
const uint8_t  kPinBtnInputOpMode   = D8;
const uint32_t kInputOpModeDuration = 3000; // ms
const uint32_t kLoopInterval        = 2000; // ms


// Exec
// ----------------------------------------------------------------------------
enum class OperationMode
{
    kDefault = 0,
    kServerless
};

OperationMode operation_mode = OperationMode::kDefault;

struct SensorsData
{
  float ds18b20_temperature;
  float tds;
  float ph;
  int   contact_water;
  float dht_temperature;
  float dht_relative_humidity;
  float bmp388_pressure;
  float bmp388_temperature;
  float bmp388_altitude;

  SensorsData()
  {
    ds18b20_temperature   = kSenErrorValue;
    tds                   = kSenErrorValue;
    ph                    = kSenErrorValue;
    contact_water         = 0;
    dht_temperature       = kSenErrorValue;
    dht_relative_humidity = kSenErrorValue;
    bmp388_pressure       = kSenErrorValue;
    bmp388_temperature    = kSenErrorValue;
    bmp388_altitude       = kSenErrorValue;
  }

  String to_json_string() const
  {
    String json_string = F("{\"tds\":");
    json_string += tds;
    json_string += F(",\"ph\":");
    json_string += ph;
    json_string += F(",\"ds18b20_temperature\":");
    json_string += ds18b20_temperature;
    json_string += F(",\"dht_temperature\":");
    json_string += dht_temperature;
    json_string += F(",\"dht_relative_humidity\":");
    json_string += dht_relative_humidity;
    json_string += F(",\"bmp388_pressure\":");
    json_string += bmp388_pressure;
    json_string += F(",\"bmp388_temperature\":");
    json_string += bmp388_temperature;
    json_string += F(",\"bmp388_altitude\":");
    json_string += bmp388_altitude;
    json_string += F(",\"contact_water\":");
    json_string += contact_water;
    json_string += F("}");
    return json_string;
  }
};

SensorsData sensors_data;

OneWire one_wire(kOneWireBus);
DallasTemperature sen_ds18b20(&one_wire);
DHT sen_dht(kDhtPin, kDhtType);
BMP388_DEV bmp388(4, 5); // SDA, SCL

Adafruit_SSD1306 display(
  kDisplayWidth, kDisplayHeight, &Wire, kDisplayOledReset);

WiFiClient wifi_client;
MqttClient mqtt_client(wifi_client);

unsigned long prev_ms = 0;


float get_tds_cqr_value(const float temperature = 25.0)
{
  const float compens_coef  = 0.02 * (temperature - 25.0) + 1.0;
  const int16_t adc         = ads.readADC_SingleEnded(kAdsTdsIdx);
  const float v             = ads.computeVolts(adc) / compens_coef;
  return (133.42 * pow(v, 3) - 255.86 * pow(v, 2) + 857.39 * v) / 2;
}


float get_ph_value()
{
  const int16_t adc         = ads.readADC_SingleEnded(kAdsTdsIdx);
  const float v             = ads.computeVolts(adc);
  return v;
}


void update_sensors_data()
{
  // Water
  sen_ds18b20.requestTemperatures();
  sensors_data.ds18b20_temperature = sen_ds18b20.getTempCByIndex(0);
  sensors_data.tds = get_tds_cqr_value(sensors_data.ds18b20_temperature);
  sensors_data.ph = get_ph_value();
  // sensors_data.contact_water = digitalRead(kCtcWtrPin);

  // Air
  sensors_data.dht_relative_humidity = sen_dht.readHumidity();
  sensors_data.dht_temperature       = sen_dht.readTemperature();

  const uint8_t res_bmp388 = bmp388.getMeasurements(
    sensors_data.bmp388_temperature,
    sensors_data.bmp388_pressure,
    sensors_data.bmp388_altitude
  );

  if (!res_bmp388)
  {
    sensors_data.bmp388_temperature  = kSenErrorValue;
    sensors_data.bmp388_pressure     = kSenErrorValue;
    sensors_data.bmp388_altitude     = kSenErrorValue;
  }
}


void display_sensors_data()
{
  display.clearDisplay();
  display.setCursor(0, 0);

  // Test - size 1: rot(1|3) == 10 char / line; rot(0|2): 20 char / line.
  //display.println(F("012345678901234567890123456789"));

  display.println(F("---- WATER"));
  display.print(sensors_data.ds18b20_temperature);
  display.println(F("*C"));
  display.print(sensors_data.tds);
  display.println(F("ppm"));
  display.print(F("pH: "));
  display.println(sensors_data.ph);
  display.print(F("ctc_wtr: "));
  display.println(sensors_data.contact_water);
  display.println();
  display.println(F("------ AIR"));
  display.print(sensors_data.dht_temperature);
  display.println(F("*C"));
  display.print(F("RH: "));
  display.print(sensors_data.dht_relative_humidity);
  display.println(F("%"));
  display.println();
  display.println(F("------ BMP"));
  display.print(sensors_data.bmp388_pressure);
  display.println(F("hPa"));
  display.print(sensors_data.bmp388_temperature);
  display.println(F("*C"));
  display.print(sensors_data.bmp388_altitude);
  display.println(F("m"));

  // Test - available lines, in case of overflow: 2
  //display.println(F("line 1"));
  //display.println(F("line 2"));

  display.display();
}


void publish_data()
{
  String json_string = sensors_data.to_json_string();
  Serial.println(json_string);

  if (operation_mode != OperationMode::kServerless)
  {
    mqtt_client.beginMessage(kMqttTopic);
    mqtt_client.print(json_string);
    mqtt_client.endMessage();
  }
}


void set_operation_mode_from_input()
{
  digitalWrite(kPinLedInputOpMode, LOW);

  Serial.print(F("Hit button to set serverless mode, else wait... ms left: "));
  Serial.println(kInputOpModeDuration);

  bool res                      = false;
  unsigned long ms_init         = millis();
  unsigned long ms_since_start  = millis();

  while (ms_since_start - ms_init < kInputOpModeDuration)
  {
    ms_since_start = millis();
    if (digitalRead(kPinBtnInputOpMode))
    {
      operation_mode = OperationMode::kServerless;
      break;
    }
    delay(100);
  }

  digitalWrite(kPinLedInputOpMode, HIGH);
}


void setup()
{
  Serial.begin(115200);
  Serial.println();

  pinMode(kPinLedInputOpMode, OUTPUT);
  pinMode(kPinBtnInputOpMode, INPUT);
  set_operation_mode_from_input();

  // Sensors
  ads.setGain(GAIN_TWOTHIRDS);  // (dflt) +-6.144 V
  ads.begin();
  sen_ds18b20.begin();
  sen_dht.begin();
  bmp388.begin(BMP388_I2C_ALT_ADDR);              // Sets BMP388 in SLEEP_MODE
  bmp388.setTimeStandby(TIME_STANDBY_1280MS);     // Set standby time
  bmp388.startNormalConversion();                 // Set NORMAL_MODE
  // pinMode(kCtcWtrPin, INPUT_PULLUP); WIRE WITH PULL(UP|DOWN) RESISTOR

  // Display
  if (!display.begin(SSD1306_SWITCHCAPVCC, kDisplayAddress))
  {
    Serial.println(F("Error setup: display.begin"));
    for (;;);
  }
  display.setRotation(3);
  display.setTextSize(1);
  display.setTextColor(SSD1306_WHITE);
  display.cp437(true);

  // Server
  if (operation_mode != OperationMode::kServerless)
  {
    Serial.print(F("Connecting to Access Point..."));
    WiFi.begin(kApSsid, kApPassword);
    while (WiFi.status() != WL_CONNECTED)
    {
      delay(500);
      Serial.print(F("."));
    }
    Serial.println();
    Serial.print(F("Connection to AP successful, IP address: "));
    Serial.println(WiFi.localIP());

    Serial.print(F("Connecting to MQTT Broker... "));
    Serial.println(kMqttHost);
    mqtt_client.setId(kMqttClientID);
    mqtt_client.setUsernamePassword(kMqttUser, kMqttPassword);

    if (!mqtt_client.connect(kMqttHost, kMqttPort))
    {
      Serial.print(F("MQTT connection failed. Error code: "));
      Serial.println(mqtt_client.connectError());
      for (;;);
    }
    Serial.println(F("Connection to MQTT Broker successful."));
  }
  else
  {
    Serial.println(F("Running in serverless mode."));
  }
  Serial.println();
}


void loop()
{
  const unsigned long ms_since_start = millis();
  if (ms_since_start - prev_ms >= kLoopInterval)
  {
    prev_ms = ms_since_start;
    update_sensors_data();
    display_sensors_data();
    publish_data();
  }
}
