import asyncio

from jeelink import available_ports, setup, PCAJeeLink


async def main():
    pca = await setup(available_ports()[0])
    if pca.available:
        pca.request_devices()
    await asyncio.sleep(100)


if __name__ == '__main__':
    asyncio.run(main())
