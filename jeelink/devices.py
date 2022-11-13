from datetime import datetime


class PCADevice:
    def __init__(self, jeelink, device_id):
        self._jeelink = jeelink
        self._id = device_id
        self._state = 0
        self._power = 0
        self._consumption = 0
        self._channel = 0
        self._last_update = None

    @property
    def state(self):
        return self._state

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

    def turn_on(self):
        self._send_command(command=5, data=0)

    def turn_off(self):
        self._send_command(command=5, data=1)

    def status_request(self):
        self._send_command(command=4, data=0)

    def reset(self):
        self._send_command(command=4, data=1)

    def identify(self):
        self._send_command(command=6, data=0)

    def _send_command(self, command, data):
        address = f"{int(self._id[:3])},{int(self._id[3:6])},{int(self._id[6:])}"
        self._jeelink.write(f"{self._channel},{command},{address},{data},255,255,255,255s")

    def get_updates(self, data):
        self._channel = data["channel"]
        self._state = data["state"]
        self._power = data["power"]
        self._consumption = data["consumption"]
        self._last_update = datetime.now()
