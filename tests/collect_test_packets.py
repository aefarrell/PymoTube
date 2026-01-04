# Some simple functions for connecting to an Atmotube Pro for testing purposes

import asyncio
from bleak import BleakClient, BleakScanner
from atmotube import AtmoTube_PRO_UUID

ATMOTUBE = "C2:2B:42:15:30:89"  # the mac address of my Atmotube

async def get_client(mac):
    device = await BleakScanner.find_device_by_address(mac)
    if not device:
        raise Exception("Device not found")

    client = BleakClient(device)
    await client.connect()
    return client

async def collect_data(mac, queue, collection_time):
    async def status_cb(char, data):
        await queue.put(("status byte", data))

    async def sps30_cb(char, data):
        await queue.put(("sps30 byte", data))

    async def bme280_cb(char, data):
        await queue.put(("bme280 byte", data))

    async def sgp30_cb(char, data):
        await queue.put(("sgp30 byte", data))

    device = await BleakScanner.find_device_by_address(mac)
    if not device:
        raise Exception("Device not found")

    async with BleakClient(device) as client:
        asyncio.gather(*[client.start_notify(AtmoTube_PRO_UUID.SPS30, sps30_cb),
        client.start_notify(AtmoTube_PRO_UUID.STATUS, status_cb),
        client.start_notify(AtmoTube_PRO_UUID.BME280, bme280_cb),
        client.start_notify(AtmoTube_PRO_UUID.SGPC3, sgp30_cb)])
        await asyncio.sleep(collection_time)
        await queue.put(None)


def main():
    mac = ATMOTUBE
    collection_time = 10  # seconds
    queue = asyncio.Queue()

    async def runner():
        collector = asyncio.create_task(
            collect_data(mac, queue, collection_time)
            )
        while True:
            item = await queue.get()
            if item is None:
                break
            print(f"Received: {item[0]}, Data: {item[1]}")
        await collector

    asyncio.run(runner())


if __name__ == "__main__":
    main()
