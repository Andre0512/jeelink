import asyncio
import logging
import re
import sys

logging.basicConfig(stream=sys.stdout, level=logging.DEBUG,
                    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s")
_LOGGER = logging.getLogger(__name__)


def jeelink_register(cls):
    cls._pattern = {}
    for method_name in dir(cls):
        method = getattr(cls, method_name)
        if hasattr(method, '_prop'):
            cls._pattern.update({method_name: method._prop})
    return cls


def jeelink_pattern(*args):
    def wrapper(func):
        func._prop = args
        return func

    return wrapper


@jeelink_register
class JeeLink(asyncio.Protocol):
    def __init__(self, device_class):
        self._data = ""
        self._model = ""
        self._available = False
        self._writer = None
        self._device_class = device_class
        self._devices = {}
        self._handlers = []

    @property
    def available(self):
        return self._available

    @property
    def devices(self):
        return self._devices

    @property
    def model(self):
        return self._model

    @property
    def device_class(self):
        return self._device_class

    def set_device_class(self, device_class):
        self._device_class = device_class

    def set_available(self, available):
        self._available = available
        for device in self._devices.values():
            device.set_available(available)

    async def wait_available(self, timeout=10):
        waited = 0
        while not self.available and waited <= timeout:
            await asyncio.sleep(0.1)
            waited += 0.1
        if not self.available:
            raise TimeoutError

    def _process_data(self, read_data):
        for line in read_data.replace("\r", "").split("\n"):
            if line:
                _LOGGER.debug(f"Read  - {line}")
                for func, pattern in self._pattern.items():
                    if result := re.findall(pattern[0], line):
                        getattr(self, func)(result)

    def data_received(self, data: bytes) -> None:
        self._data = self._data + data.decode()
        if not self._data[-2:] == "\r\n":
            return
        try:
            self._process_data(self._data)
        finally:
            self._data = ""

    def connection_lost(self, exc):
        _LOGGER.error("Removed jeelink")
        self.set_available(False)

    def connection_made(self, transport):
        _LOGGER.info("Connected with jeelink")
        self._writer = transport
        self.set_available(True)

    def _write(self, text):
        _LOGGER.debug(f"Write - {text}")
        self._writer.write(text.encode())

    def _add_device(self, device_id):
        if device_id not in self._devices:
            self._devices[device_id] = self._device_class(self, device_id)

    @jeelink_pattern('\\[(.+?)]')
    def model_parser(self, result):
        self._model = result[0]
        if not self._available:
            self.set_available(True)
