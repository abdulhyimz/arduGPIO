#include <ArduinoJson.h>

namespace {
const unsigned long SERIAL_TIMEOUT_MS = 250;
const size_t INPUT_BUFFER_SIZE = 160;

void sendStatusOk() {
  StaticJsonDocument<64> response;
  response["status"] = "OK";
  serializeJson(response, Serial);
  Serial.println();
}

void sendValueOk(int value) {
  StaticJsonDocument<96> response;
  response["status"] = "OK";
  response["value"] = value;
  serializeJson(response, Serial);
  Serial.println();
}

void sendError(const char* message) {
  StaticJsonDocument<128> response;
  response["status"] = "ERROR";
  response["message"] = message;
  serializeJson(response, Serial);
  Serial.println();
}

bool readPin(const JsonDocument& doc, int& pin) {
  if (!doc.containsKey("pin") || !doc["pin"].is<int>()) {
    sendError("Missing or invalid pin");
    return false;
  }

  pin = doc["pin"].as<int>();
  if (pin < 0) {
    sendError("Pin must be >= 0");
    return false;
  }

  return true;
}
}

void setup() {
  Serial.begin(9600);
  Serial.setTimeout(SERIAL_TIMEOUT_MS);
}

void loop() {
  if (Serial.available() <= 0) {
    return;
  }

  char inputBuffer[INPUT_BUFFER_SIZE];
  size_t bytesRead = Serial.readBytesUntil('\n', inputBuffer, INPUT_BUFFER_SIZE - 1);

  if (bytesRead == 0) {
    return;
  }

  inputBuffer[bytesRead] = '\0';
  while (bytesRead > 0 && (inputBuffer[bytesRead - 1] == '\r' || inputBuffer[bytesRead - 1] == ' ' || inputBuffer[bytesRead - 1] == '\t')) {
    inputBuffer[bytesRead - 1] = '\0';
    bytesRead--;
  }

  StaticJsonDocument<256> doc;
  DeserializationError error = deserializeJson(doc, inputBuffer);
  if (error) {
    sendError("Invalid JSON");
    return;
  }

  if (!doc.containsKey("action") || !doc["action"].is<const char*>()) {
    sendError("Missing or invalid action");
    return;
  }

  const char* action = doc["action"];
  int pin = -1;

  if (strcmp(action, "SETUP") == 0) {
    if (!readPin(doc, pin)) {
      return;
    }
    if (!doc.containsKey("mode") || !doc["mode"].is<const char*>()) {
      sendError("Missing or invalid mode");
      return;
    }

    const char* mode = doc["mode"];
    if (strcmp(mode, "OUTPUT") == 0) {
      pinMode(pin, OUTPUT);
      sendStatusOk();
    } else if (strcmp(mode, "INPUT") == 0) {
      pinMode(pin, INPUT);
      sendStatusOk();
    } else {
      sendError("Invalid mode");
    }
    return;
  }

  if (strcmp(action, "WRITE") == 0) {
    if (!readPin(doc, pin)) {
      return;
    }
    if (!doc.containsKey("value") || !doc["value"].is<const char*>()) {
      sendError("Missing or invalid value");
      return;
    }

    const char* value = doc["value"];
    if (strcmp(value, "HIGH") == 0) {
      digitalWrite(pin, HIGH);
      sendStatusOk();
    } else if (strcmp(value, "LOW") == 0) {
      digitalWrite(pin, LOW);
      sendStatusOk();
    } else {
      sendError("Invalid value");
    }
    return;
  }

  if (strcmp(action, "READ") == 0) {
    if (!readPin(doc, pin)) {
      return;
    }
    sendValueOk(digitalRead(pin));
    return;
  }

  if (strcmp(action, "ANALOG_READ") == 0) {
    if (!readPin(doc, pin)) {
      return;
    }
    sendValueOk(analogRead(pin));
    return;
  }

  if (strcmp(action, "ANALOG_WRITE") == 0) {
    if (!readPin(doc, pin)) {
      return;
    }
    if (!doc.containsKey("value") || !doc["value"].is<int>()) {
      sendError("Missing or invalid value");
      return;
    }

    int value = doc["value"].as<int>();
    if (value < 0 || value > 255) {
      sendError("Invalid PWM value (must be between 0 and 255)");
      return;
    }

    analogWrite(pin, value);
    sendStatusOk();
    return;
  }

  sendError("Invalid command");
}
