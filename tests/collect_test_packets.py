# This is a simple script to open a connection to an Atmotube device,
# collect data for a specified duration, and print the received data packets.
# Convenient for generating byte arrays for testing.

import asyncio
from bleak import BleakClient, BleakScanner
from atmotube import AtmoTube_GATT_UUIDs

ATMOTUBE = "C2:2B:42:15:30:89"  # the mac address of my Atmotube


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
        await client.start_notify(AtmoTube_GATT_UUIDs.SPS30, sps30_cb)
        await client.start_notify(AtmoTube_GATT_UUIDs.STATUS, status_cb)
        await client.start_notify(AtmoTube_GATT_UUIDs.BME280, bme280_cb)
        await client.start_notify(AtmoTube_GATT_UUIDs.SGPC3, sgp30_cb)
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
