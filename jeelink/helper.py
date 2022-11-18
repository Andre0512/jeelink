import asyncio

import serial_asyncio
from serial.tools import list_ports

from jeelink.pca import PCAJeeLink


def available_ports():
    return [port[0] for port in sorted(list_ports.comports())]


async def setup(self, port, baud=57600):
    loop = asyncio.get_event_loop()
    _, jeelink = await serial_asyncio.create_serial_connection(loop, PCAJeeLink, port, baudrate=baud)
    return jeelink
