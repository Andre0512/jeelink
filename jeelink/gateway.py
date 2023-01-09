import asyncio
import logging
import sys

logging.basicConfig(stream=sys.stdout, level=logging.DEBUG,
                    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s")
_LOGGER = logging.getLogger(__name__)


class JeeLink(asyncio.Protocol):
    def __init__(self):
        self._data = ""
        self._model = ""
        self._available = False
        self._writer = None

    @property
    def available(self):
        return self._available

    def set_available(self, available):
        self._available = available

    @property
    def model(self):
        return self._model

    async def wait_available(self, timeout=10):
        waited = 0
        while not self.available and waited <= timeout:
            await asyncio.sleep(0.1)
            waited += 0.1
        if not self.available:
            raise TimeoutError

    def _process_data(self, data):
        raise NotImplemented

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

