# arduGPIO

Python + Arduino JSON serial bridge for simple GPIO-style control.

## Features

- Pin mode setup (`INPUT`, `OUTPUT`)
- Digital write/read (`HIGH`, `LOW`, `0/1`)
- Analog read
- PWM write (`0..255`)
- Line-based JSON protocol between Python and Arduino

## Requirements

- Python 3.8+
- Arduino IDE
- ArduinoJson library on the board side
- A board flashed with `arduino.ino`

## Install

### From source

```bash
git clone https://github.com/abdulhyimz/arduGPIO.git
cd arduGPIO
python -m pip install -e .
```

### Runtime dependency

`pyserial` is installed automatically from package metadata.

## Arduino setup

1. Open `arduino.ino` in Arduino IDE.
2. Install **ArduinoJson** from Library Manager.
3. Select your board/port and upload.
4. Keep baud rate at `9600` (default firmware/client setting).

## Serial port examples

- **Windows:** `COM3`
- **Linux:** `/dev/ttyUSB0` or `/dev/ttyACM0`
- **macOS:** `/dev/tty.usbmodem*` or `/dev/tty.usbserial*`

## Python API

```python
from arduGPIO import arduGPIO

with arduGPIO(port="COM3", baudrate=9600, timeout=1.0, write_timeout=1.0) as gpio:
    gpio.setup(9, "OUTPUT")
    gpio.output(9, "HIGH")
    gpio.output(9, "LOW")

    gpio.setup(5, "INPUT")
    state = gpio.input(5)

    value = gpio.analogRead(0)
    gpio.analogWrite(9, 128)
```

### Notes about compatibility

- Existing class/method names are preserved: `arduGPIO`, `setup`, `output`, `input`, `analogRead`, `analogWrite`, `close`.
- Added improvements:
  - Context manager support (`with ... as ...`)
  - Input validation
  - Explicit read/write timeouts
  - Clear connection/protocol exceptions

## Protocol

Each command is one JSON object per line (`\n` terminated).

Supported actions:

- `SETUP`: `{"action":"SETUP","pin":9,"mode":"OUTPUT"}`
- `WRITE`: `{"action":"WRITE","pin":9,"value":"HIGH"}`
- `READ`: `{"action":"READ","pin":5}`
- `ANALOG_READ`: `{"action":"ANALOG_READ","pin":0}`
- `ANALOG_WRITE`: `{"action":"ANALOG_WRITE","pin":9,"value":128}`

Responses:

- Success: `{"status":"OK"}` or `{"status":"OK","value":123}`
- Error: `{"status":"ERROR","message":"..."}`

The firmware uses a bounded serial timeout and fixed input buffer for safer parsing.

## Limitations and PWM notes

- PWM support depends on board/pin capabilities.
- Pin numbering and analog pin behavior are board-specific.
- This project does not auto-detect board pin capabilities.

## Development and testing

Run tests (no hardware required):

```bash
python -m pip install -e . pytest
pytest
```

Build package locally:

```bash
python -m pip install --upgrade build
python -m build
```

Hardware integration checks must be run manually with a connected Arduino.

## License

MIT (see `LICENSE`).
