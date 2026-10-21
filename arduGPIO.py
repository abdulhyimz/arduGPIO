"""arduGPIO Python client.

This module provides a small JSON-over-serial client for controlling an Arduino
running the companion ``arduino.ino`` firmware.
"""

from __future__ import annotations

import json
import time
from typing import Any, Dict, Optional

import serial
from serial import SerialException


class ArduGPIOError(Exception):
    """Base exception for arduGPIO client errors."""


class ArduGPIOConnectionError(ArduGPIOError):
    """Raised when serial connection fails or is unavailable."""


class ArduGPIOProtocolError(ArduGPIOError):
    """Raised for malformed, empty, or error protocol responses."""


class ArduGPIOTimeoutError(ArduGPIOProtocolError):
    """Raised when no response is received before timeout."""


class ArduGPIO:
    """JSON-over-serial client for the ``arduino.ino`` protocol.

    Args:
        port: Serial port path (for example ``COM3`` or ``/dev/ttyUSB0``).
        baudrate: Serial baud rate (default: 9600).
        timeout: Read timeout in seconds.
        write_timeout: Write timeout in seconds.
        startup_delay: Delay after opening serial to allow board reset.
    """

    VALID_MODES = {"INPUT", "OUTPUT"}
    VALID_DIGITAL_VALUES = {"HIGH", "LOW"}

    def __init__(
        self,
        port: str,
        baudrate: int = 9600,
        timeout: float = 1.0,
        write_timeout: float = 1.0,
        startup_delay: float = 2.0,
    ) -> None:
        if not isinstance(port, str) or not port.strip():
            raise ValueError("port must be a non-empty string")
        if not isinstance(baudrate, int) or baudrate <= 0:
            raise ValueError("baudrate must be a positive integer")
        if timeout is None or timeout <= 0:
            raise ValueError("timeout must be a positive number")
        if write_timeout is None or write_timeout <= 0:
            raise ValueError("write_timeout must be a positive number")
        if startup_delay < 0:
            raise ValueError("startup_delay must be >= 0")

        self._closed = False
        try:
            self.ser = serial.Serial(
                port=port,
                baudrate=baudrate,
                timeout=timeout,
                write_timeout=write_timeout,
            )
        except SerialException as exc:
            raise ArduGPIOConnectionError(f"Unable to open serial port {port!r}: {exc}") from exc

        time.sleep(startup_delay)

    def __enter__(self) -> "ArduGPIO":
        return self

    def __exit__(self, exc_type: Any, exc: Any, tb: Any) -> None:
        self.close()

    @staticmethod
    def _validate_pin(pin: int) -> int:
        if not isinstance(pin, int):
            raise ValueError("pin must be an integer")
        if pin < 0:
            raise ValueError("pin must be >= 0")
        return pin

    def _ensure_open(self) -> None:
        if self._closed or self.ser is None or not self.ser.is_open:
            raise ArduGPIOConnectionError("Serial connection is closed")

    def send_command(self, command: Dict[str, Any]) -> Dict[str, Any]:
        """Send a command dictionary and return the parsed JSON response."""
        self._ensure_open()

        if not isinstance(command, dict):
            raise ValueError("command must be a dictionary")

        try:
            payload = json.dumps(command, separators=(",", ":")) + "\n"
            self.ser.write(payload.encode("utf-8"))
            self.ser.flush()
        except (SerialException, OSError) as exc:
            raise ArduGPIOConnectionError(f"Failed to send command: {exc}") from exc

        try:
            response_raw = self.ser.readline()
        except (SerialException, OSError) as exc:
            raise ArduGPIOConnectionError(f"Failed to read response: {exc}") from exc

        if not response_raw:
            raise ArduGPIOTimeoutError("Timed out waiting for response from Arduino")

        response_text = response_raw.decode("utf-8", errors="replace").strip()
        if not response_text:
            raise ArduGPIOProtocolError("Received empty response from Arduino")

        try:
            response = json.loads(response_text)
        except json.JSONDecodeError as exc:
            raise ArduGPIOProtocolError(f"Malformed JSON response: {response_text!r}") from exc

        if not isinstance(response, dict):
            raise ArduGPIOProtocolError("Response must be a JSON object")

        status = response.get("status")
        if status == "ERROR":
            message = response.get("message", "Unknown error")
            raise ArduGPIOProtocolError(str(message))
        if status != "OK":
            raise ArduGPIOProtocolError(f"Unexpected response status: {status!r}")

        return response

    def setup(self, pin: int, mode: str) -> None:
        """Set pin mode to ``INPUT`` or ``OUTPUT``."""
        self._validate_pin(pin)
        if not isinstance(mode, str):
            raise ValueError("mode must be a string")
        normalized_mode = mode.upper()
        if normalized_mode not in self.VALID_MODES:
            raise ValueError("Invalid mode. Use 'INPUT' or 'OUTPUT'.")

        self.send_command({"action": "SETUP", "pin": pin, "mode": normalized_mode})

    def output(self, pin: int, value: str) -> None:
        """Write digital value ``HIGH`` or ``LOW`` to a pin."""
        self._validate_pin(pin)
        if not isinstance(value, str):
            raise ValueError("value must be a string")
        normalized_value = value.upper()
        if normalized_value not in self.VALID_DIGITAL_VALUES:
            raise ValueError("Invalid value. Use 'HIGH' or 'LOW'.")

        self.send_command({"action": "WRITE", "pin": pin, "value": normalized_value})

    def input(self, pin: int) -> int:
        """Read digital value from a pin."""
        self._validate_pin(pin)
        response = self.send_command({"action": "READ", "pin": pin})
        if "value" not in response:
            raise ArduGPIOProtocolError("Missing 'value' in READ response")
        return int(response["value"])

    def analog_read(self, pin: int) -> int:
        """Read analog value from a pin."""
        self._validate_pin(pin)
        response = self.send_command({"action": "ANALOG_READ", "pin": pin})
        if "value" not in response:
            raise ArduGPIOProtocolError("Missing 'value' in ANALOG_READ response")
        return int(response["value"])

    def analogRead(self, pin: int) -> int:
        """Compatibility alias for :meth:`analog_read`."""
        return self.analog_read(pin)

    def analog_write(self, pin: int, value: int) -> None:
        """Write PWM value (0..255) to a pin."""
        self._validate_pin(pin)
        if not isinstance(value, int):
            raise ValueError("PWM value must be an integer.")
        if value < 0 or value > 255:
            raise ValueError("PWM value must be between 0 and 255.")

        self.send_command({"action": "ANALOG_WRITE", "pin": pin, "value": value})

    def analogWrite(self, pin: int, value: int) -> None:
        """Compatibility alias for :meth:`analog_write`."""
        self.analog_write(pin, value)

    def close(self) -> None:
        """Close the serial connection. Safe to call multiple times."""
        if self._closed:
            return
        self._closed = True
        try:
            if self.ser is not None and self.ser.is_open:
                self.ser.close()
        except (SerialException, OSError) as exc:
            raise ArduGPIOConnectionError(f"Failed to close serial connection: {exc}") from exc


class arduGPIO(ArduGPIO):
    """Backward-compatible class name alias."""
