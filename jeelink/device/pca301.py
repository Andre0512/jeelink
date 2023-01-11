import logging
import time

from jeelink.device.device import JeeLinkDevice

_LOGGER = logging.getLogger(__name__)


class PCADevice(JeeLinkDevice):
    def __init__(self, jeelink, device_id):
        super().__init__(jeelink, device_id)
        self._state = None
        self._power = None
        self._consumption = None
        self._channel = 0

    @property
    def power(self):
        return self._power

    @property
    def consumption(self):
        return self._consumption

    @property
    def channel(self):
        return self._channel

    @property
    def state(self):
        return self._state

    def turn_off(self):
        self._state = False
        self._jeelink.send_command(self._id, self._channel, command=5, data=0)

    def status_request(self):
        self._jeelink.send_command(self._id, self._channel, command=4, data=0)

    def reset(self):
        self._jeelink.send_command(self._id, self._channel, command=4, data=1)

    def identify(self):
        self._jeelink.send_command(self._id, self._channel, command=6, data=0)
