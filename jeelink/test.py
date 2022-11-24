import asyncio

from jeelink import available_ports, setup, PCAJeeLink, is_pca


async def main():
    print(await is_pca(available_ports()[0]))

    await asyncio.sleep(100)


if __name__ == '__main__':
    asyncio.run(main())
