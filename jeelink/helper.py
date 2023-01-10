import asyncio
import logging

import serial_asyncio
from serial import SerialException
from serial.tools import list_ports

from jeelink.gateway import JeeLink
from jeelink.sketch.lacrosse import LaCrosseJeeLink
from jeelink.sketch.pca301 import PCAJeeLink

_LOGGER = logging.getLogger(__name__)


def available_ports():
    return [port[0] for port in sorted(list_ports.comports())]


async def setup(port, baud=57600, device_class=JeeLink, timeout=10):
    jeelink = await connect(port, baud, device_class)
    if not device_class == JeeLink:
        return jeelink
    time = 0
    while not (model := jeelink.model) and time < timeout:
        await asyncio.sleep(0.01)
        time += 0.01
    if "pcaSerial" in model:
        jeelink = await connect(port, baud, PCAJeeLink)
    elif "lacrosse" in model:
        jeelink = await connect(port, baud, LaCrosseJeeLink)
    return jeelink


async def connect(port, baud=57600, device_class=JeeLink, timeout=10):
    loop = asyncio.get_event_loop()
    try:
        _, jeelink = await serial_asyncio.create_serial_connection(loop, device_class, port, baudrate=baud)
    except SerialException as e:
        _LOGGER.error(e)
        raise ConnectionError
    await jeelink.wait_available(timeout=timeout)
    return jeelink


async def is_pca(port, baud=57600, device_class=PCAJeeLink, timeout=10):
    jeelink = await setup(port, baud, device_class)
    if jeelink:
        try:
            await jeelink.wait_available(timeout=timeout/2)
        except TimeoutError:
            return False
        waited = 0
        jeelink.request_version()
        while not jeelink.model and waited <= timeout/2:
            await asyncio.sleep(0.1)
            waited += 0.1
        if jeelink.model:
            return "pcaSerial" in jeelink.model
    return False
