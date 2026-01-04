# Some simple functions for connecting to an Atmotube Pro for testing purposes
import asyncio
from bleak import BleakClient, BleakScanner
from atmotube import AtmotubeProGATT_UUID

ATMOTUBE = "C2:2B:42:15:30:89"  # the mac address of my Atmotube


async def get_client(mac):
    device = await BleakScanner.find_device_by_address(mac)
    if not device:
        raise Exception("Device not found")

    client = BleakClient(device)
    await client.connect()
    return client


async def collect_broadcast_data(mac, queue, collection_time):
    async def callback(device, advertising_data):
        if device.address.upper() == mac.upper():
            await queue.put((device, advertising_data))

    async with BleakScanner(callback):
        await asyncio.sleep(collection_time)
        await queue.put(None)

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
        asyncio.gather(*[
            client.start_notify(AtmotubeProGATT_UUID.SPS30, sps30_cb),
            client.start_notify(AtmotubeProGATT_UUID.STATUS, status_cb),
            client.start_notify(AtmotubeProGATT_UUID.BME280, bme280_cb),
            client.start_notify(AtmotubeProGATT_UUID.SGPC3, sgp30_cb)
        ])
        await asyncio.sleep(collection_time)
        await queue.put(None)

async def runner(mac, queue, collection_time, collector):
    task = asyncio.create_task(
        collector(mac, queue, collection_time)
        )
    while True:
        item = await queue.get()
        if item is None:
            break
        device, adv_data = item
        #print(f"Received: {item[0]}, Data: {item[1]}")
        print(f"{device.name}")
    await task

def main():
    mac = ATMOTUBE
    collection_time = 60  # seconds
    queue = asyncio.Queue()
    collector = collect_broadcast_data
    asyncio.run(runner(mac, queue, collection_time, collector))


if __name__ == "__main__":
    main()
