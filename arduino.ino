#include <ArduinoJson.h>

void setup() {
  Serial.begin(9600);
}

void loop() {
  if (Serial.available() > 0) {
    String jsonCommand = Serial.readStringUntil('\n');
    jsonCommand.trim();  // Remove extra spaces

    // Parse JSON
    StaticJsonDocument<200> doc;
    DeserializationError error = deserializeJson(doc, jsonCommand);

    if (error) {
      Serial.println("{\"status\":\"ERROR\",\"message\":\"Invalid JSON\"}");
      return;
    }

    // Process commands
    String action = doc["action"];
    int pin = doc["pin"];

    if (action == "SETUP") {
      String mode = doc["mode"];
      if (mode == "OUTPUT") {
        pinMode(pin, OUTPUT);
        Serial.println("{\"status\":\"OK\"}");
      } else if (mode == "INPUT") {
        pinMode(pin, INPUT);
        Serial.println("{\"status\":\"OK\"}");
      } else {
        Serial.println("{\"status\":\"ERROR\",\"message\":\"Invalid mode\"}");
      }
    } else if (action == "WRITE") {
      String value = doc["value"];
      if (value == "HIGH") {
        digitalWrite(pin, HIGH);
        Serial.println("{\"status\":\"OK\"}");
      } else if (value == "LOW") {
        digitalWrite(pin, LOW);
        Serial.println("{\"status\":\"OK\"}");
      } else {
        Serial.println("{\"status\":\"ERROR\",\"message\":\"Invalid value\"}");
      }
    } else if (action == "READ") {
      int state = digitalRead(pin);
      Serial.println("{\"status\":\"OK\",\"value\":" + String(state) + "}");
    } else if (action == "ANALOG_READ") {
      int value = analogRead(pin);
      Serial.println("{\"status\":\"OK\",\"value\":" + String(value) + "}");
    } else if (action == "ANALOG_WRITE") {
      int value = doc["value"];
      if (value >= 0 && value <= 255) {
        analogWrite(pin, value);
        Serial.println("{\"status\":\"OK\"}");
      } else {
        Serial.println("{\"status\":\"ERROR\",\"message\":\"Invalid PWM value (must be between 0 and 255)\"}");
      }
    } else {
      Serial.println("{\"status\":\"ERROR\",\"message\":\"Invalid command\"}");
    }
  }
}
