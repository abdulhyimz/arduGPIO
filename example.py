from arduGPIO import arduGPIO
import time

# Set the port where your Arduino is connected (e.g., 'COM3' or '/dev/ttyUSB0')
arduino = arduGPIO(port='COM3', baudrate=9600)

print("Connected to Arduino. Starting tests...\n")

# 1. Pin Mode Setup (SETUP)
print("1. Setting pin modes...")
arduino.setup(9, 'OUTPUT')  # Set pin 9 as OUTPUT
arduino.setup(5, 'INPUT')   # Set pin 5 as INPUT
print("-> Pin 9 set as OUTPUT, Pin 5 set as INPUT.\n")

# 2. Digital Write (WRITE)
print("2. Testing digital write...")
arduino.output(9, 'HIGH')  # Set pin 9 to HIGH
print("-> Pin 9 set to HIGH.")
time.sleep(2)  # Wait 2 seconds
arduino.output(9, 'LOW')   # Set pin 9 to LOW
print("-> Pin 9 set to LOW.\n")

# 3. Digital Read (READ)
print("3. Testing digital read...")
state = arduino.input(5)  # Read the state of pin 5
print(f"-> Digital state of pin 5: {state}\n")

# 4. Analog Read (ANALOG_READ)
print("4. Testing analog read...")
analog_value = arduino.analogRead(0)  # Read analog value from A0
print(f"-> Analog value on A0: {analog_value}\n")

# 5. Analog Write (ANALOG_WRITE) - PWM
print("5. Testing analog write (PWM)...")
for brightness in range(0, 256):  # Fade in from 0 to 255
    arduino.analogWrite(9, brightness)  # Set PWM value on pin 9
    print(f"-> Pin 9 PWM value: {brightness}")
    time.sleep(0.01)  # Wait 10 ms
for brightness in range(255, -1, -1):  # Fade out from 255 to 0
    arduino.analogWrite(9, brightness)  # Set PWM value on pin 9
    print(f"-> Pin 9 PWM value: {brightness}")
    time.sleep(0.01)  # Wait 10 ms
print("-> PWM test completed.\n")

print("All tests completed successfully!")

# Close the connection
arduino.close()
print("Arduino connection closed.")
