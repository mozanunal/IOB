/*
 *  This sketch sends data via HTTP GET requests to data.sparkfun.com service.
 *
 *  You need to get streamId and privateKey at data.sparkfun.com and paste them
 *  below. Or just customize this script to talk to other HTTP servers.
 *
 */

#include <ESP8266WiFi.h>
#include <ArduinoJson.h>

const char* ssid     = "BABALAR";
const char* password = "24939300";

const char* host = "207.154.195.207";
const char* streamId   = "....................";
const char* privateKey = "....................";

StaticJsonBuffer<200> jsonBuffer;

JsonObject& root = jsonBuffer.createObject();
JsonObject& data = root.createNestedObject("data");

void setup() {
  Serial.begin(115200);
  delay(10);

  // We start by connecting to a WiFi network

  Serial.println();
  Serial.println();
  Serial.print("Connecting to ");
  Serial.println(ssid);
  
  WiFi.begin(ssid, password);
  
  while (WiFi.status() != WL_CONNECTED) {
    delay(500);
    Serial.print(".");
  }

  Serial.println("");
  Serial.println("WiFi connected");  
  Serial.println("IP address: ");
  Serial.println(WiFi.localIP());
}

void loop() {
  delay(1000);

  unsigned int adc_uv = analogRead(A0);
  Serial.print("ADC value: "); Serial.println(adc_uv);

  Serial.print("connecting to ");
  Serial.println(host);
  
  // Use WiFiClient class to create TCP connections
  WiFiClient client;
  const int httpPort = 8080;
  if (!client.connect(host, httpPort)) {
    Serial.println("connection failed");
    return;
  }

 
  
  root["UUID"] = "1";

  data["uv"] = (float)(adc_uv / 1024);
  data["temprature"] = "28";
  data["temprature_sea"] = "18";
  data["ph"] = "7.4";
  data["wave_ratio"] = "0.2";
  data["cloudness"] = "0.3";
 
  root.prettyPrintTo(Serial);
  
  // We now create a URI for the request
  String url = "/rest";
  
  Serial.print("Requesting URL: ");
  Serial.println(url);
  
  // This will send the request to the server
  client.println("POST /rest HTTP/1.1");
  client.print("Host: "); client.print(host); client.print(":"); client.println("8080");
  client.println("Accept: */*");
  client.println("Content-Type: application/json");
  client.print("Content-Length: "); client.println(root.measureLength());
  client.println("Connection: close");
  client.println();
  root.printTo(client);

  unsigned long timeout = millis();
  while (client.available() == 0) {
    if (millis() - timeout > 5000) {
      Serial.println(">>> Client Timeout !");
      client.stop();
      return;
    }
  }
  
  // Read all the lines of the reply from server and print them to Serial
  while(client.available()){
    String line = client.readStringUntil('\r');
    Serial.print(line);
  }
  
  Serial.println();
  Serial.println("closing connection");
}

