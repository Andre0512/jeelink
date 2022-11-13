import asyncio
import logging
import re
import sys

logging.basicConfig(stream=sys.stdout, level=logging.DEBUG,
                    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s")
_LOGGER = logging.getLogger(__name__)

class JeeLinkReader(asyncio.Protocol):
    def __init__(self):
        self._data = ""
        self._chunk = ""

    def _process_data(self, data):
        pass

    def data_received(self, data: bytes) -> None:
        data = data.decode()
        if not data[-2:] == "\r\n":
            self._chunk = data
            return
        self._data = self._chunk + data
        self._process_data(self._data)
        self._chunk = ""

    def connection_lost(self, exc):
        _LOGGER.error("Removed jeelink-python")


class PCAJeeLinkReader(JeeLinkReader):
    def __init__(self):
        super().__init__()
        self._model = ""
        self._callback = None

    def _process_data(self, read_data):
        for line in read_data.split("\n"):
            line = line.replace("\r", "")
            if not line:
                continue
            if match := re.findall("OK 24 (\\d+) \\d((?: \\d+){3})((?: \\d+){5})", line):
                channel, address, data = match[0]
                data = [int(value) for value in data.split(" ") if value]
                device_id = "".join([f"{chunk:>03}" for chunk in address.split(" ") if chunk])
                device_data = {"power": (int(data[1]) * 256 + int(data[2])) / 10.0, "state": int(data[0]),
                               "consumption": (int(data[3]) * 256 + int(data[4])) / 100.0, "channel": int(channel)}
                if self._callback:
                    self._callback(device_id, data=device_data)
            elif match := re.findall("L 24 (\\d+) \\d :(?: \\d+){2}((?: \\d+){3})(?: \\d+){5}", line):
                if self._callback:
                    self._callback("".join([f"{chunk:>03}" for chunk in match[0][1]]), intern_number=match[0][0])
            elif not self._model and (model := re.findall('\\[(.+?)]', line)):
                self._model = model
            _LOGGER.debug(f"Read  - {line}")

    def register_callback(self, method):
        self._callback = method

