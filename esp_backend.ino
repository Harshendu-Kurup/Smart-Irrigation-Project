#include <WiFi.h>
#include <HTTPClient.h>
#include <WiFiClientSecure.h>
#include <ArduinoJson.h>
#include "DHT.h"

// ================= FEATURE FLAGS =================
#define ENABLE_PUMP true
#define ENABLE_WATER_SENSOR true
// =================================================

// -------- WIFI --------
const char* ssid = "FTTH-D0E6";
const char* password = "vinod21087";

// -------- BACKEND URL (RENDER = HTTPS) --------
String backendURL = "https://smart-irrigation-project-7oky.onrender.com/sensor-data";

// -------- WEATHER API --------
String weatherAPIKey = "ddddec6f094f8cbdc75eb7f15445c786";
float latitude = 9.4567178;
float longitude = 76.5256168;

// -------- SENSORS --------
#define DHTPIN 4
#define DHTTYPE DHT22
DHT dht(DHTPIN, DHTTYPE);

int soilPin  = 34;
int lightPin = 35;

// -------- OPTIONAL HARDWARE --------
#define RELAY_PIN 26
#define WATER_LEVEL_PIN 32

// ================= SETUP =================
void setup() {
  Serial.begin(115200);
  delay(1000);

  Serial.println("\n🔌 Connecting to WiFi...");
  WiFi.begin(ssid, password);

  while (WiFi.status() != WL_CONNECTED) {
    Serial.print(".");
    delay(400);
  }

  Serial.println("\n✅ WiFi Connected");
  Serial.print("📡 ESP IP: ");
  Serial.println(WiFi.localIP());

  dht.begin();

  pinMode(RELAY_PIN, OUTPUT);
  digitalWrite(RELAY_PIN, LOW);
}

// ================= LOOP =================
void loop() {

  if (WiFi.status() != WL_CONNECTED) {
    Serial.println("❌ WiFi lost! Reconnecting...");
    WiFi.reconnect();
    delay(2000);
    return;
  }

  // -------- SENSOR READINGS --------
  float temp = dht.readTemperature();
  float hum  = dht.readHumidity();
  if (isnan(temp)) temp = 0;
  if (isnan(hum))  hum  = 0;

  int soilRaw  = analogRead(soilPin);
  int lightRaw = analogRead(lightPin);

  float soilMoisture = map(soilRaw, 4095, 1500, 0, 100);
  soilMoisture = constrain(soilMoisture, 0, 100);

  // -------- WATER LEVEL (ALWAYS SEND) --------
  float waterLevel = 100;   // default SAFE value

  if (ENABLE_WATER_SENSOR) {
    int waterRaw = analogRead(WATER_LEVEL_PIN);
    waterLevel = map(waterRaw, 4095, 0, 0, 100);
    waterLevel = constrain(waterLevel, 0, 100);
  }

  // -------- WEATHER FETCH --------
  float apiTemp = 0.0;
  int apiHumidity = 0;
  String weatherDesc = "unknown";

  String weatherURL =
    "http://api.openweathermap.org/data/2.5/weather?lat=" +
    String(latitude) + "&lon=" + String(longitude) +
    "&appid=" + weatherAPIKey + "&units=metric";

  HTTPClient weatherHttp;
  weatherHttp.begin(weatherURL);
  int weatherCode = weatherHttp.GET();

  if (weatherCode == 200) {
    DynamicJsonDocument wdoc(1024);
    deserializeJson(wdoc, weatherHttp.getString());

    apiTemp = wdoc["main"]["temp"].as<float>();   
    apiHumidity = wdoc["main"]["humidity"].as<int>();
    weatherDesc = wdoc["weather"][0]["description"].as<String>();
  }

  weatherHttp.end();

  // -------- CREATE JSON --------
  DynamicJsonDocument doc(512);
  doc["soil_moisture"] = soilMoisture;
  doc["temperature"]  = temp;
  doc["humidity"]     = hum;
  doc["light"]        = lightRaw;
  doc["water_level"]  = waterLevel;    
  doc["api_temp"]     = apiTemp;
  doc["api_humidity"] = apiHumidity;
  doc["weather_desc"] = weatherDesc;

  String jsonData;
  serializeJson(doc, jsonData);

  Serial.println("\n📤 Sending JSON:");
  Serial.println(jsonData);

  // -------- SEND TO BACKEND --------
  WiFiClientSecure client;
  client.setInsecure();

  HTTPClient http;
  http.begin(client, backendURL);
  http.setTimeout(10000);
  http.addHeader("Content-Type", "application/json");

  int code = http.POST(jsonData);

  if (code > 0) {
    String response = http.getString();
    Serial.print("✅ Backend Code: ");
    Serial.println(code);
    Serial.println("📥 Backend Reply:");
    Serial.println(response);

    DynamicJsonDocument resDoc(256);
    if (deserializeJson(resDoc, response) == DeserializationError::Ok) {
      int pumpCmd = resDoc["pump"] | 0;

      if (ENABLE_PUMP && pumpCmd == 1) {
        digitalWrite(RELAY_PIN, LOW);
        Serial.println("🚰 Pump ON");
      } else {
        digitalWrite(RELAY_PIN, HIGH);
        Serial.println("🚫 Pump OFF");
      }
    }

  } else {
    Serial.print("❌ HTTP POST FAILED: ");
    Serial.println(code);
  }

  http.end();
  delay(180000);
}
