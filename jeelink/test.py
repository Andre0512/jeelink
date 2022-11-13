import asyncio

from pca import PCA


async def main():
    pca = PCA()
    await pca.open(pca.available_ports()[0])
    #while not pca.devices:
    #    await asyncio.sleep(0.1)
    #device = list(pca.devices)[0]
    #pca.send_command()
    await asyncio.sleep(10000)


if __name__ == '__main__':
    asyncio.run(main())
