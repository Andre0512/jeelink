import asyncio

import pypca


async def main():
    pca = pypca.PCA()
    await pca.open(pca.available_ports()[0])
    await asyncio.sleep(100)
    pca.devices[list(pca.devices)[0]].turn_on()
    await asyncio.sleep(10000)


if __name__ == '__main__':
    asyncio.run(main())
