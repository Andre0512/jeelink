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


def serialize(device_id):
    return f"{int(device_id[:3])} {int(device_id[3:6])} {int(device_id[6:])}"


def deserialize(device_id):
    return "".join([f"{chunk:>03}" for chunk in device_id.split(" ") if chunk])
