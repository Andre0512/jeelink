import asyncio
import logging
import re

import serial_asyncio
from serial import SerialException
from serial.tools import list_ports

from jeelink.gateway import JeeLink, jeelink_sketches, JEELINK_DEVICES

_LOGGER = logging.getLogger(__name__)


def available_ports():
    return [port[0] for port in sorted(list_ports.comports())]


def jeelink_devices():
    result = []
    for port in list_ports.comports():
        if ids := re.findall("VID:PID=(\\d+):(\\d+)", port.hwid):
            vid, pid = ids[0]
            for device in JEELINK_DEVICES:
                if pid == device["pid"] and vid == device["vid"]:
                    result.append(port[0])
    return result


async def discover(port="", baud=57600, device_class=JeeLink, timeout=10):
    port = port or jeelink_devices()[0]
    jeelink = await setup(port, baud, device_class)
    if not device_class == JeeLink:
        return jeelink
    time = 0
    while not (model := jeelink.model) and time < timeout:
        await asyncio.sleep(0.01)
        time += 0.01
    for pattern, sketch in jeelink_sketches.items():
        if re.findall(pattern, model):
            return await setup(port, baud, sketch)


async def setup(port, baud=57600, device_class=JeeLink, timeout=10):
    loop = asyncio.get_event_loop()
    try:
        _, jeelink = await serial_asyncio.create_serial_connection(loop, device_class, port, baudrate=baud)
    except SerialException as e:
        _LOGGER.error(e)
        raise ConnectionError
    await jeelink.wait_available(timeout=timeout)
    return jeelink
