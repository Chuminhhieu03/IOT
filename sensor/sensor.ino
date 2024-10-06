#include <WiFi.h>              
#include <DHT.h>
#include <ArduinoJson.h>
#include <PubSubClient.h>
#include <WiFiClientSecure.h>

#define DHTPIN 18
#define DHTTYPE DHT11

DHT dht(DHTPIN, DHTTYPE);

const char* ssid = "Phong Tro 402";      // Wifi connect
const char* password = "12345678";   // Password

const char* mqtt_server = "7135442a5e904296bf8f44f17ea3feec.s1.eu.hivemq.cloud";
const int mqtt_port = 8883;
const char* mqtt_username = "tienhiep345";  // User
const char* mqtt_password = "Hiep2003"; // Password
//---------------------------------------------------

WiFiClientSecure espClient;
PubSubClient client(espClient);

unsigned long lastMsg = 0;
#define MSG_BUFFER_SIZE (50)
char msg[MSG_BUFFER_SIZE];

void setup_wifi() {
  delay(10);
  Serial.println();
  Serial.print("Connecting to ");
  Serial.println(ssid);
  WiFi.begin(ssid, password);

  while (WiFi.status() != WL_CONNECTED) {
    delay(500);
    Serial.print(".");
  }
  randomSeed(micros());
  Serial.println("");
  Serial.println("WiFi connected");
  Serial.println("IP address: ");
  Serial.println(WiFi.localIP());
}

// ------------Connect to MQTT Broker-----------------------------
void reconnect() {
  while (!client.connected()) {
    Serial.print("Attempting MQTT connection...");
    String clientID = "ESPClient-";
    clientID += String(random(0xffff), HEX);
    if (client.connect(clientID.c_str(), mqtt_username, mqtt_password)) {
      Serial.println("connected");
      client.subscribe("esp32/client");
    } else {
      Serial.print("failed, rc=");
      Serial.print(client.state());
      Serial.println(" try again in 5 seconds");
      delay(5000);
    }
  }
}

//-----Call back Method for Receiving MQTT message---------
void callback(char* topic, byte* payload, unsigned int length) {
  String incommingMessage = "";
  for (int i = 0; i < length; i++) incommingMessage += (char)payload[i];
  Serial.println("Message arrived [" + String(topic) + "]" + incommingMessage);
}

//-----Method for Publishing MQTT Messages---------
void publishMessage(const char* topic, String payload, boolean retained) {
  if (client.publish(topic, payload.c_str(), true))
    Serial.println("Message published [" + String(topic) + "]: " + payload);
}

void setup() {
  Serial.begin(9600);
  while (!Serial) delay(1);

  dht.begin();

  setup_wifi();
  espClient.setInsecure();
  client.setServer(mqtt_server, mqtt_port);
  client.setCallback(callback);
}

unsigned long timeUpdate = millis();

void loop() {
  if (!client.connected()) {
    reconnect();
  }
  client.loop();

  // Read DHT11 sensor
  if (millis() - timeUpdate > 5000) {
    float h = dht.readHumidity();
    float t = dht.readTemperature();
    Serial.println("Nhiệt độ: " + String(t));
    Serial.println("Độ ẩm: "+ String(h));

    DynamicJsonDocument doc(1024);
    doc["humidity"] = h;
    doc["temperature"] = t;
    char mqtt_message[128];
    serializeJson(doc, mqtt_message);
    publishMessage("topic/dht", mqtt_message, true);

    timeUpdate = millis();
  }
}
