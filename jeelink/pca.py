import asyncio
import logging
import sys

import serial_asyncio
from jeelink.devices import PCADevice
from jeelink.reader import PCAJeeLinkReader
from serial.tools import list_ports

logging.basicConfig(stream=sys.stdout, level=logging.DEBUG,
                    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s")
_LOGGER = logging.getLogger(__name__)

class PCA:
    def __init__(self):
        """Initialize the pca device."""
        self._baud = 57600
        self._port = ""
        self._model = ""
        self._reader = None
        self._writer = None
        self._devices = {}

    @staticmethod
    def available_ports():
        return [port[0] for port in sorted(list_ports.comports())]

    async def open(self, port):
        self._port = port
        self._writer, self._reader = await serial_asyncio.create_serial_connection(asyncio.get_event_loop(),
                                                                                   PCAJeeLinkReader,
                                                                                   self._port, baudrate=self._baud)
        self._reader.register_callback(self._get_updates)
        await asyncio.sleep(5)
        self.write("l")
        self.write("v")
        # Turn off the blue LED
        self.write("0a")

    @property
    def devices(self):
        return self._devices

    def _get_updates(self, device_id, data=None, intern_number=0):
        if intern_number:
            self.write(f"{intern_number}p")
            return
        if device_id not in self._devices:
            self._devices[device_id] = PCADevice(self, device_id)
        self._devices[device_id].get_updates(data)

    def write(self, text):
        _LOGGER.debug(f"Write - {text}")
        self._writer.write(text.encode())
