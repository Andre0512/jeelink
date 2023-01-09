import logging

from jeelink import helper
from jeelink.device.pca301 import PCADevice
from jeelink.gateway import JeeLink, jeelink_register, jeelink_pattern

_LOGGER = logging.getLogger(__name__)


@jeelink_register
class PCAJeeLink(JeeLink):
    def __init__(self, device_class=PCADevice):
        """Initialize the pca device."""
        super().__init__(device_class)

    def send_command(self, device_id, channel_id, command, data):
        address = helper.serialize(device_id).replace(" ", ",")
        self._write(f"{channel_id},{command},{address},{data},255,255,255,255s")

    @jeelink_pattern(f"OK 24 (\\d+) 4((?: \\d+){3})((?: \\d+){5})")
    def _pca_data(self, data):
        self.set_available(True)
        self._device_data(*data[0])

    @jeelink_pattern(f"L 24 (\\d+) \\d : (\\d+) 4((?: \\d+){3})((?: \\d+){5})")
    def _requested_device(self, data):
        number, channel, address, data = data[0]
        self.force_polling(number)
        self._add_device(helper.deserialize(address))
        self._device_data(channel, address, data)

    def _device_data(self, channel, address, raw_data):
        if device := self._devices.get(helper.deserialize(address)):
            data = [int(value) for value in raw_data.split(" ") if value]
            device.set_state(int(data[0]))
            device.set_power((int(data[1]) * 256 + int(data[2])) / 10.0)
            device.set_consumption((int(data[3]) * 256 + int(data[4])) / 100.0)
            device.set_channel(int(channel))
        else:
            self._add_device(helper.deserialize(address))
            self._device_data(channel, address, raw_data)

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

    def set_available(self, available):
        super().set_available(available)
        if not self._devices:
            self._init_connection()

    def _init_connection(self):
        self.request_version()
        self.set_led_off()
        self.request_devices()
