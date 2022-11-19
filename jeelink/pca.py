import asyncio
import logging
import re
import sys

from jeelink.gateway import JeeLink
from jeelink import helper

logging.basicConfig(stream=sys.stdout, level=logging.DEBUG,
                    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s")
_LOGGER = logging.getLogger(__name__)


class PCAJeeLink(JeeLink):
    def __init__(self):
        """Initialize the pca device."""
        super().__init__()
        self._model = ""
        self._devices = []
        self._event_callbacks = {}
        self._discover_callbacks = []
        self._started = False

    @property
    def model(self):
        return self._model

    @property
    def started(self):
        return self._started

    @property
    def devices(self):
        return self._devices

    @property
    def available(self):
        return self._available

    @available.setter
    def available(self, available):
        self._available = available
        if not available:
            for device, callbacks in self._event_callbacks.items():
                for callback in callbacks:
                    callback({})
        else:
            self._init_connection()

    def _process_data(self, read_data):
        for line in read_data.split("\n"):
            line = line.replace("\r", "")
            if not line:
                continue
            _LOGGER.debug(f"Read  - {line}")
            if match := re.findall("OK 24 (\\d+) 4((?: \\d+){3})((?: \\d+){5})", line):
                channel, address, data = match[0]
                data = [int(value) for value in data.split(" ") if value]
                device_data = {"power": (int(data[1]) * 256 + int(data[2])) / 10.0, "state": int(data[0]),
                               "consumption": (int(data[3]) * 256 + int(data[4])) / 100.0, "channel": int(channel)}
                for callback in self._event_callbacks.get(helper.deserialize(address), []):
                    callback(device_data)
                self._add_device(helper.deserialize(match[0][1]))
                if not self._started:
                    self._available = True
            elif match := re.findall("L 24 (\\d+) \\d :(?: \\d+){2}((?: \\d+){3})(?: \\d+){5}", line):
                self.force_polling(match[0][0])
                self._add_device(helper.deserialize(match[0][1]))
            elif not self._model and (model := re.findall('\\[(.+?)]', line)):
                self._model = model
            elif not self._started and "Available commands" in line:
                self._available = True

    def _add_device(self, device_id, data=None):
        if device_id not in self._devices:
            self._devices.append(device_id)
            for callback in self._discover_callbacks:
                callback(device_id, data=data)

    def request_devices(self):
        self._write("l")

    def request_version(self):
        self._write("v")

    def set_led_off(self):
        """ Turn on/off the blue LED """
        self._write("0a")

    def set_led_on(self):
        """ Turn on/off the blue LED """
        self._write("1a")

    def force_polling(self, number):
        self._write(f"{number}p")

    def send_command(self, device_id, channel_id, command, data):
        address = helper.serialize(device_id).replace(" ", ",")
        self._write(f"{channel_id},{command},{address},{data},255,255,255,255s")

    def register_event_callback(self, device_id, callback):
        self._event_callbacks.setdefault(device_id, []).append(callback)

    def register_discover_callback(self, callback):
        self._discover_callbacks.append(callback)
        for device_id in self._devices:
            callback(device_id)

    def _init_connection(self):
        self._started = True
        self.request_version()
        self.set_led_off()
        self.request_devices()
