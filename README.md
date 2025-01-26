# arduGPIO

![Arduino and Python](https://encrypted-tbn0.gstatic.com/images?q=tbn:ANd9GcQoKnoHZFuIwEy9_rQHoYH-JxEHAvdN1AFuPw&s)

A Python library to control Arduino using JSON-based serial communication. This library supports digital and analog operations, including PWM, making it perfect for IoT projects, robotics, and automation.

---

## Features

- **Set pin modes**: Configure pins as `INPUT` or `OUTPUT`.
- **Digital read/write**: Read from or write to digital pins.
- **Analog read**: Read analog values from analog pins.
- **PWM (analog write)**: Control PWM pins with values between 0 and 255.

---

## Requirements

- **Arduino IDE**: Upload the provided Arduino sketch to your board.
- **Python 3.x**: Ensure Python is installed on your system.
- **Libraries**:
  - `pyserial`: Install via `pip install pyserial`.
  - `ArduinoJson` (for Arduino): Install via Arduino Library Manager.

---

## Installation

1. **Arduino Setup**:
   - Upload the `arduino.ino` sketch to your Arduino.
   - Ensure the baud rate is set to **9600**.

2. **Python Setup**:
   - Clone this repository or download the `arduGPIO.py` file.
   - Install the required Python library:
     ```bash
     pip install pyserial
     ```

---

## Arduino Code

Upload the arduino.ino file to your Arduino and it's ready to use
