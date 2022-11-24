import asyncio
import logging
import re
import sys

from jeelink import helper, PCADevice
from jeelink.gateway import JeeLink

logging.basicConfig(stream=sys.stdout, level=logging.INFO,
                    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s")
_LOGGER = logging.getLogger(__name__)


class PCAJeeLink(JeeLink):
    def __init__(self, device_class=PCADevice):
        """Initialize the pca device."""
        super().__init__()
        self._model = ""
        self._devices = {}
        self._device_class = device_class
        self._pattern = "(\\d+) 4((?: \\d+){3})((?: \\d+){5})"

    @property
    def model(self):
        return self._model

    @property
    def devices(self):
        return self._devices

    @property
    def available(self):
        return self._available

    def set_available(self, available):
        self._available = available
        for device in self._devices.values():
            device.set_available(available)
        if not self._devices:
            self._init_connection()

    async def wait_available(self, timeout=10):
        waited = 0
        while not self.available and waited <= timeout:
            await asyncio.sleep(0.1)
            waited += 0.1
        if not self.available:
            raise TimeoutError

    @property
    def device_class(self):
        return self._device_class

    def set_device_class(self, device_class):
        self._device_class = device_class

    def _process_data(self, read_data):
        for line in read_data.replace("\r", "").split("\n"):
            if line:
                _LOGGER.debug(f"Read  - {line}")
                if match := re.findall(f"OK 24 {self._pattern}", line):
                    self.set_available(True)
                    self._device_data(*match[0])
                elif match := re.findall(f"L 24 (\\d+) \\d : {self._pattern}", line):
                    number, channel, address, data = match[0]
                    self.force_polling(number)
                    self._add_device(helper.deserialize(address))
                    self._device_data(channel, address, data)
                elif not self._model and (model := re.findall('\\[(.+?)]', line)):
                    self._model = model[0]
                elif not self._available and "Available commands" in line:
                    self.set_available(True)

    def _device_data(self, channel, address, data):
        if device := self._devices.get(helper.deserialize(address)):
            data = [int(value) for value in data.split(" ") if value]
            device.set_state(int(data[0]))
            device.set_power((int(data[1]) * 256 + int(data[2])) / 10.0)
            device.set_consumption((int(data[3]) * 256 + int(data[4])) / 100.0)
            device.set_channel(int(channel))
        else:
            self._add_device(helper.deserialize(address))

    def _add_device(self, device_id):
        if device_id not in self._devices:
            self._devices[device_id] = self._device_class(self, device_id)

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

    def _init_connection(self):
        self.request_version()
        self.set_led_off()
        self.request_devices()
