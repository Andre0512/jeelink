import asyncio
import logging
import re
import sys

from jeelink import JeeLink

logging.basicConfig(stream=sys.stdout, level=logging.DEBUG,
                    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s")
_LOGGER = logging.getLogger(__name__)


class PCAJeeLink(JeeLink):
    def __init__(self):
        """Initialize the pca device."""
        super().__init__()
        self._model = ""
        self._reader = None
        self._writer = None
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

    @staticmethod
    def _parse_device_id(device_id):
        return "".join([f"{chunk:>03}" for chunk in device_id.split(" ") if chunk])

    def _process_data(self, read_data):
        for line in read_data.split("\n"):
            line = line.replace("\r", "")
            if not line:
                continue
            if match := re.findall("OK 24 (\\d+) 4((?: \\d+){3})((?: \\d+){5})", line):
                channel, address, data = match[0]
                data = [int(value) for value in data.split(" ") if value]
                device_data = {"power": (int(data[1]) * 256 + int(data[2])) / 10.0, "state": int(data[0]),
                               "consumption": (int(data[3]) * 256 + int(data[4])) / 100.0, "channel": int(channel)}
                self._get_updates(self._parse_device_id(address), data=device_data)
                self._started = True
            elif match := re.findall("L 24 (\\d+) \\d :(?: \\d+){2}((?: \\d+){3})(?: \\d+){5}", line):
                self._get_updates(self._parse_device_id(match[0][1]), intern_number=match[0][0])
            elif not self._model and (model := re.findall('\\[(.+?)]', line)):
                self._model = model
            elif not self._started and "Available commands" in line:
                self._started = True
            _LOGGER.debug(f"Read  - {line}")

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
        address = f"{int(device_id[:3])},{int(device_id[3:6])},{int(device_id[6:])}"
        self._write(f"{channel_id},{command},{address},{data},255,255,255,255s")

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

    def register_event_callback(self, device_id, callback):
        self._event_callbacks.setdefault(device_id, []).append(callback)

    def register_discover_callback(self, callback):
        self._discover_callbacks.append(callback)
        for device_id in self._devices:
            callback(device_id)

    def connection_made(self, transport):
        super(PCAJeeLink, self).connection_made(transport)
        while not self._reader.started:
            asyncio.run(asyncio.sleep(0.01))
        self.request_version()
        self.set_led_off()
        self.request_devices()
