import asyncio

import serial_asyncio
from serial.tools import list_ports

from jeelink.pca import PCAJeeLink


def available_ports():
    return [port[0] for port in sorted(list_ports.comports())]


async def setup(port, baud=57600, device_class=PCAJeeLink):
    loop = asyncio.get_event_loop()
    _, jeelink = await serial_asyncio.create_serial_connection(loop, device_class, port, baudrate=baud)
    return jeelink


async def is_pca(port, baud=57600, device_class=PCAJeeLink, timeout=10):
    jeelink = await setup(port, baud, device_class)
    try:
        await jeelink.wait_available(timeout=timeout/2)
    except TimeoutError:
        return False
    waited = 0
    jeelink.request_version()
    while not jeelink.model and waited <= timeout/2:
        await asyncio.sleep(0.1)
        waited += 0.1
    if not jeelink.model:
        return False
    return "pcaSerial" in jeelink.model


def serialize(device_id):
    return f"{int(device_id[:3])} {int(device_id[3:6])} {int(device_id[6:])}"


def deserialize(device_id):
    return "".join([f"{chunk:>03}" for chunk in device_id.split(" ") if chunk])
