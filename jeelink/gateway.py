import asyncio
import logging
import sys

logging.basicConfig(stream=sys.stdout, level=logging.INFO,
                    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s")
_LOGGER = logging.getLogger(__name__)


class JeeLink(asyncio.Protocol):
    def __init__(self):
        self._data = ""
        self._chunk = ""
        self._available = False
        self._writer = None

    @property
    def available(self):
        return self._available

    def set_available(self, available):
        self._available = available

    def _process_data(self, data):
        pass

    def data_received(self, data: bytes) -> None:
        data = data.decode()
        if not data[-2:] == "\r\n":
            self._chunk = data
            return
        self._data = self._chunk + data
        self._process_data(self._data)
        self._chunk = ""

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
