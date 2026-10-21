"""Example usage for arduGPIO.

Update SERIAL_PORT before running.
"""

import time

from arduGPIO import arduGPIO

SERIAL_PORT = "COM3"  # Windows example. Linux/macOS: '/dev/ttyUSB0' or '/dev/tty.usbmodem*'


with arduGPIO(port=SERIAL_PORT, baudrate=9600) as arduino:
    print("Connected to Arduino")

    arduino.setup(9, "OUTPUT")
    arduino.setup(5, "INPUT")

    arduino.output(9, "HIGH")
    time.sleep(1)
    arduino.output(9, "LOW")

    state = arduino.input(5)
    print(f"Digital state of pin 5: {state}")

    analog_value = arduino.analogRead(0)
    print(f"Analog value on A0: {analog_value}")

    print("Running short PWM ramp on pin 9...")
    for brightness in range(0, 256, 16):
        arduino.analogWrite(9, brightness)
        time.sleep(0.03)
    for brightness in range(255, -1, -16):
        arduino.analogWrite(9, brightness)
        time.sleep(0.03)

print("Arduino connection closed")
