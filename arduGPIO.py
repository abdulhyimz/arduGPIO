import serial
import time
import json

class arduGPIO:
    def __init__(self, port, baudrate=9600):
        self.ser = serial.Serial(port, baudrate)
        time.sleep(2)  # Wait for Arduino to initialize

    def send_command(self, command):
        self.ser.write((json.dumps(command) + '\n').encode())
        response = self.ser.readline().decode().strip()
        return json.loads(response)

    def setup(self, pin, mode):
        if mode not in ['INPUT', 'OUTPUT']:
            raise ValueError("Invalid mode. Use 'INPUT' or 'OUTPUT'.")
        command = {"action": "SETUP", "pin": pin, "mode": mode}
        response = self.send_command(command)
        if response["status"] != "OK":
            raise ValueError(response.get("message", "Unknown error"))

    def output(self, pin, value):
        if value not in ['HIGH', 'LOW']:
            raise ValueError("Invalid value. Use 'HIGH' or 'LOW'.")
        command = {"action": "WRITE", "pin": pin, "value": value}
        response = self.send_command(command)
        if response["status"] != "OK":
            raise ValueError(response.get("message", "Unknown error"))

    def input(self, pin):
        command = {"action": "READ", "pin": pin}
        response = self.send_command(command)
        if response["status"] == "OK":
            return response["value"]
        else:
            raise ValueError(response.get("message", "Unknown error"))

    def analogRead(self, pin):
        command = {"action": "ANALOG_READ", "pin": pin}
        response = self.send_command(command)
        if response["status"] == "OK":
            return response["value"]
        else:
            raise ValueError(response.get("message", "Unknown error"))

    def analogWrite(self, pin, value):
        if value < 0 or value > 255:
            raise ValueError("PWM value must be between 0 and 255.")
        command = {"action": "ANALOG_WRITE", "pin": pin, "value": value}
        response = self.send_command(command)
        if response["status"] != "OK":
            raise ValueError(response.get("message", "Unknown error"))

    def close(self):
        self.ser.close()
