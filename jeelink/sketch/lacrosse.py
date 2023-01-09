import logging

from jeelink import JeeLink
from jeelink.device.lacrosse import LaCrosseDevice
from jeelink.gateway import jeelink_pattern, jeelink_register

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


@jeelink_register
class LaCrosseJeeLink(JeeLink):
    def __init__(self, device_class=LaCrosseDevice):
        super().__init__(device_class)

    @jeelink_pattern("OK 9 (\\d+) (\\d+) (\\d+) (\\d+) (\\d+)")
    def _temperature(self, data):
        data = [int(c) for c in data[0]]
        print(data)
        sensor_id = data[0]
        sensor_type = data[1] & 0x7f
        new_battery = True if data[1] & 0x80 else False
        temperature = float(data[2] * 256 + data[3] - 1000) / 10
        humidity = data[4] & 0x7f
        low_battery = True if data[4] & 0x80 else False
