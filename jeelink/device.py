import logging

_LOGGER = logging.getLogger(__name__)


class PCADevice:
    def __init__(self, jeelink, device_id):
        self._jeelink = jeelink
        self._id = device_id
        self._state = None
        self._power = 0
        self._consumption = 0
        self._channel = 0
        self._last_update = None
        self._jeelink.register_event_callback(self._id, self.get_updates)
        self._available = False

    @property
    def available(self):
        return self._available

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
    def last_update(self):
        return self._last_update

    def set_on(self):
        self._state = True
        self._jeelink.send_command(self._id, self._channel, command=5, data=1)

    def set_off(self):
        self._state = False
        self._jeelink.send_command(self._id, self._channel, command=5, data=0)

    def status_request(self):
        self._jeelink.send_command(self._id, self._channel, command=4, data=0)

    def reset(self):
        self._jeelink.send_command(self._id, self._channel, command=4, data=1)

    def identify(self):
        self._jeelink.send_command(self._id, self._channel, command=6, data=0)

    def get_updates(self, data):
        _LOGGER.error(str(data))
        if data:
            self._channel = data["channel"]
            self._state = bool(data["state"])
            self._power = data["power"]
            self._consumption = data["consumption"]
        self._available = bool(data)
