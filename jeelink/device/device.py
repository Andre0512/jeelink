import asyncio
import logging
import time

_LOGGER = logging.getLogger(__name__)

UPDATE_INTERVAL_SECONDS = 30


class JeeLinkDevice:
    def __init__(self, jeelink, device_id):
        self._jeelink = jeelink
        self._id = device_id
        self._last_update = time.time()
        self._available = True
        self._name = f"{jeelink.__class__.__name__}.{self._id}"

    @property
    def id(self):
        return self._id

    @property
    def name(self):
        return self._name

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
    def last_update(self):
        return time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(self._last_update))

    async def _set_unavailable(self):
        while self._last_update > (time.time() - UPDATE_INTERVAL_SECONDS * 10):
            await asyncio.sleep(UPDATE_INTERVAL_SECONDS)
        self.set_available(False)
        _LOGGER.warning(f"Set {self._name} unavailable")

    def close(self):
        for task in asyncio.all_tasks(asyncio.get_event_loop()):
            if task.get_name() == f"{self._name} available check" and not task.cancelled():
                task.cancel()

    def device_update(self, **kwargs):
        self._last_update = time.time()
        for key, value in kwargs.items():
            if not hasattr(self, key):
                raise AttributeError
            setattr(self, f"_{key}", value)
