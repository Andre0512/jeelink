import logging

from jeelink.device.lacrosse import LaCrosseDevice
from jeelink.gateway import JeeLink, jeelink_pattern, jeelink_register

_LOGGER = logging.getLogger(__name__)

"""
<n>a     set to 0 if the blue LED bothers
<n>c     use one of the possible data rates (for transmit on RFM #1)
<n>d     set to 1 to see debug messages
<n>f     initial frequency in kHz (5 kHz steps, 860480 ... 879515) 
<n>h     altituide above sea level
<n>m     bits 1: 17.241 kbps, 2 : 9.579 kbps, 4 : 8.842 kbps (for RFM #1)
<n>M     bits 1: 17.241 kbps, 2 : 9.579 kbps, 4 : 8.842 kbps (for RFM #2)
<n>o     set HF-parameter e.g. 50305o for RFM12 or 1,4o for RFM69
<n>p     transmitted the payload on the serial port 1: all, 2: only undecoded data
<n>r     use one of the possible data rates (for RFM #1)
<n>R     use one of the possible data rates (for RFM #2)
<id,..>s send the bytes to the address id
<n>t     0=no toggle, else interval in seconds (for RFM #1)
<n>T     0=no toggle, else interval in seconds (for RFM #2)
v        show version
x        test command 
<n>y     if 1 all received packets will be retransmitted  
<n>z     set to 1 to display analyzed frame data instead of the normal data
"""


@jeelink_register("LaCrosseITPlusReader")
class LaCrosseJeeLink(JeeLink):
    def __init__(self, device_class=LaCrosseDevice):
        super().__init__(device_class)

    @jeelink_pattern("OK 9 (\\d+) (\\d+) (\\d+) (\\d+) (\\d+)")
    def _temperature(self, raw_data):
        device_id, *data = [int(c) for c in raw_data[0]]
        if device := self._devices.get(device_id):
            device.device_update(**{
                "sensor_type": data[0] & 0x7f,
                "new_battery": True if data[0] & 0x80 else False,
                "temperature": float(data[1] * 256 + data[2] - 1000) / 10,
                "humidity": data[3] & 0x7f,
                "low_battery": True if data[3] & 0x80 else False,
            })
        else:
            self._add_device(device_id)
            self._temperature(raw_data)

    def set_led_off(self):
        """ Turn on the blue LED """
        self._write("0a")

    def set_led_on(self):
        """ Turn off the blue LED """
        self._write("1a")

    def request_version(self):
        self._write("v")
