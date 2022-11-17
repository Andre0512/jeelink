import asyncio
import logging
import sys

import serial_asyncio
from jeelink.reader import PCAJeeLinkReader
from serial.tools import list_ports

logging.basicConfig(stream=sys.stdout, level=logging.DEBUG,
                    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s")
_LOGGER = logging.getLogger(__name__)


def available_ports():
    return [port[0] for port in sorted(list_ports.comports())]


class PCA:
    def __init__(self):
        """Initialize the pca device."""
        self._baud = 57600
        self._port = ""
        self._model = ""
        self._reader = None
        self._writer = None
        self._devices = []
        self._event_callbacks = {}
        self._discover_callbacks = []

    async def setup(self, port):
        self._port = port
        self._writer, self._reader = await serial_asyncio.create_serial_connection(asyncio.get_event_loop(),
                                                                                   PCAJeeLinkReader,
                                                                                   self._port, baudrate=self._baud)
        self._reader.register_callback(self._get_updates)
        while not self._reader.started:
            await asyncio.sleep(0.01)
        self._write("l")
        self._write("v")
        # Turn off the blue LED
        self._write("0a")

    @property
    def devices(self):
        return self._devices

    def _get_updates(self, device_id, data=None, intern_number=0):
        if intern_number:
            self.force_polling(intern_number)
            return
        if device_id not in self._devices:
            self._devices.append(device_id)
            for cb in self._discover_callbacks:
                cb(device_id, data=data)
        else:
            for cb in self._event_callbacks.get(device_id, []):
                cb(data)

    def force_polling(self, number):
        self._write(f"{number}p")

    def _write(self, text):
        _LOGGER.debug(f"Write - {text}")
        self._writer.write(text.encode())

    def send_command(self, device_id, channel_id, command, data):
        address = f"{int(device_id[:3])},{int(device_id[3:6])},{int(device_id[6:])}"
        self._write(f"{channel_id},{command},{address},{data},255,255,255,255s")

    def register_event_callback(self, device_id, callback):
        self._event_callbacks.setdefault(device_id, []).append(callback)

    def register_discover_callback(self, callback):
        self._discover_callbacks.append(callback)
        for device_id in self._devices:
            callback(device_id)
