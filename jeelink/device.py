import asyncio
import logging
import time

_LOGGER = logging.getLogger(__name__)

UPDATE_INTERVAL_SECONDS = 30


class PCADevice:
    def __init__(self, jeelink, device_id):
        self._jeelink = jeelink
        self._id = device_id
        self._state = None
        self._power = None
        self._consumption = None
        self._channel = 0
        self._last_update = time.time()
        self._available = True
        self._name = f"PCA 301 - {self._id}"

    @property
    def name(self):
        return self._name

    @property
    def id(self):
        return self._id

    @property
    def available(self):
        return self._available

    def _available_check_running(self):
        name = f"{self._name} available check"
        if not any([name == task.get_name() for task in asyncio.all_tasks(asyncio.get_event_loop())]):
            asyncio.create_task(self._set_unavailable(), name=name)

    def set_available(self, available):
        if available:
            self._available_check_running()
        self._available = available

    @property
    def power(self):
        return self._power

    def set_power(self, power):
        self._last_update = time.time()
        self._power = power

    @property
    def consumption(self):
        return self._consumption

    def set_consumption(self, consumption):
        self._last_update = time.time()
        self._consumption = consumption

    @property
    def channel(self):
        return self._channel

    def set_channel(self, channel):
        self._last_update = time.time()
        self._channel = channel

    @property
    def state(self):
        return self._state

    def set_state(self, state):
        self._last_update = time.time()
        self._state = state

    @property
    def last_update(self):
        return self._last_update

    def turn_on(self):
        self._state = True
        self._jeelink.send_command(self._id, self._channel, command=5, data=1)

    def turn_off(self):
        self._state = False
        self._jeelink.send_command(self._id, self._channel, command=5, data=0)

    def status_request(self):
        self._jeelink.send_command(self._id, self._channel, command=4, data=0)

    def reset(self):
        self._jeelink.send_command(self._id, self._channel, command=4, data=1)

    def identify(self):
        self._jeelink.send_command(self._id, self._channel, command=6, data=0)

    async def _set_unavailable(self):
        while self._last_update > (time.time() - UPDATE_INTERVAL_SECONDS * 10):
            await asyncio.sleep(UPDATE_INTERVAL_SECONDS)
        self.set_available(False)
        logging.warning(f"Set {self.name} unavailable")

    def close(self):
        for task in asyncio.all_tasks(asyncio.get_event_loop()):
            if task.get_name() == f"{self._name} available check" and not task.cancelled():
                task.cancel()
