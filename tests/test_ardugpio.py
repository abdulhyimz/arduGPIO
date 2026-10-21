import pytest

from arduGPIO import (
    ArduGPIO,
    ArduGPIOConnectionError,
    ArduGPIOProtocolError,
    ArduGPIOTimeoutError,
    arduGPIO,
)


class FakeSerial:
    def __init__(self, *args, **kwargs):
        self.args = args
        self.kwargs = kwargs
        self.is_open = True
        self.responses = []
        self.writes = []
        self.flush_count = 0
        self.close_count = 0
        self.write_exception = None
        self.read_exception = None

    def write(self, payload):
        if self.write_exception:
            raise self.write_exception
        self.writes.append(payload)
        return len(payload)

    def flush(self):
        self.flush_count += 1

    def readline(self):
        if self.read_exception:
            raise self.read_exception
        if self.responses:
            return self.responses.pop(0)
        return b""

    def close(self):
        self.close_count += 1
        self.is_open = False


def make_client(monkeypatch, responses=None, **kwargs):
    fake = FakeSerial()
    if responses:
        fake.responses.extend(responses)

    def factory(*args, **factory_kwargs):
        fake.args = args
        fake.kwargs = factory_kwargs
        return fake

    monkeypatch.setattr("arduGPIO.serial.Serial", factory)
    client = ArduGPIO(port="COM3", startup_delay=0, **kwargs)
    return client, fake


def test_constructor_validates_arguments():
    with pytest.raises(ValueError):
        ArduGPIO(port="", startup_delay=0)
    with pytest.raises(ValueError):
        ArduGPIO(port="COM3", baudrate=0, startup_delay=0)
    with pytest.raises(ValueError):
        ArduGPIO(port="COM3", timeout=0, startup_delay=0)


def test_constructor_applies_serial_timeouts(monkeypatch):
    client, fake = make_client(monkeypatch, timeout=1.5, write_timeout=2.5)
    assert fake.kwargs["timeout"] == 1.5
    assert fake.kwargs["write_timeout"] == 2.5
    client.close()


def test_setup_command_serialization(monkeypatch):
    client, fake = make_client(monkeypatch, responses=[b'{"status":"OK"}\n'])
    client.setup(9, "OUTPUT")
    assert fake.writes[-1] == b'{"action":"SETUP","pin":9,"mode":"OUTPUT"}\n'
    client.close()


def test_input_and_analog_aliases(monkeypatch):
    client, fake = make_client(
        monkeypatch,
        responses=[b'{"status":"OK","value":1}\n', b'{"status":"OK","value":123}\n'],
    )
    assert client.input(5) == 1
    assert client.analogRead(0) == 123
    assert isinstance(arduGPIO(port="COM3", startup_delay=0), ArduGPIO)
    client.close()


def test_validation_errors(monkeypatch):
    client, _ = make_client(monkeypatch)
    with pytest.raises(ValueError):
        client.setup(-1, "OUTPUT")
    with pytest.raises(ValueError):
        client.setup(2, "BAD")
    with pytest.raises(ValueError):
        client.output(2, "MAYBE")
    with pytest.raises(ValueError):
        client.analogWrite(3, 256)
    client.close()


def test_timeout_and_empty_response_handling(monkeypatch):
    client, _ = make_client(monkeypatch, responses=[b""])
    with pytest.raises(ArduGPIOTimeoutError):
        client.setup(9, "OUTPUT")
    client.close()


def test_malformed_and_error_response_handling(monkeypatch):
    client, _ = make_client(monkeypatch, responses=[b"not-json\n"])
    with pytest.raises(ArduGPIOProtocolError):
        client.setup(9, "OUTPUT")
    client.close()

    client, _ = make_client(monkeypatch, responses=[b'{"status":"ERROR","message":"Invalid"}\n'])
    with pytest.raises(ArduGPIOProtocolError, match="Invalid"):
        client.setup(9, "OUTPUT")
    client.close()


def test_missing_value_in_read_response(monkeypatch):
    client, _ = make_client(monkeypatch, responses=[b'{"status":"OK"}\n'])
    with pytest.raises(ArduGPIOProtocolError):
        client.input(5)
    client.close()


def test_closed_connection_and_idempotent_close(monkeypatch):
    client, fake = make_client(monkeypatch)
    client.close()
    client.close()
    assert fake.close_count == 1
    with pytest.raises(ArduGPIOConnectionError):
        client.setup(9, "OUTPUT")


def test_context_manager_closes(monkeypatch):
    fake = FakeSerial()

    def factory(*args, **kwargs):
        fake.kwargs = kwargs
        return fake

    monkeypatch.setattr("arduGPIO.serial.Serial", factory)

    with ArduGPIO(port="COM3", startup_delay=0) as client:
        assert client is not None

    assert fake.is_open is False
