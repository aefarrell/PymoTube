from bleak import BleakScanner
from atmotube import (AtmotubeBLEPacket,
                      AtmotubeProBLEAdvertising,
                      AtmotubeProBLEScanResponse,
                      ble_callback_wrapper)

import asyncio
import logging


async def collect_data(queue: asyncio.Queue, collection_time: int) -> None:
    """
    Scans for Atmotube Pro BLE advertising and scan response packets for a specified time.

    :param queue: An asyncio Queue to put the received packets into
    :type queue: asyncio.Queue
    :param collection_time: The duration in seconds to collect data
    :type collection_time: int
    """
    async def callback_queue(device, packet) -> None:
        if device.name=="ATMOTUBE":
            await queue.put(packet)

    ble_callback = ble_callback_wrapper(callback_queue)
    async with BleakScanner(ble_callback):
        await asyncio.sleep(collection_time)
        await queue.put(None)


def log_ble_packet(packet: AtmotubeBLEPacket) -> None:
    """
    Logs the received packet to the console.

    :param packet: The packet to log
    :type packet: AtmotubeBLEPacket
    """
    match packet:
        case AtmotubeProBLEAdvertising():
            logging.info(f"Advertising Packet - {str(packet)}")
        case AtmotubeProBLEScanResponse():
            logging.info(f"Scan Response Packet - {str(packet)}")
        case _:
            logging.info(f"Unknown packet type")


def main() -> None:
    collection_time = 60
    queue = asyncio.Queue()

    async def runner() -> None:
        task = asyncio.create_task(
            collect_data(queue, collection_time)
            )
        while True:
            item = await queue.get()
            if item is None:
                break
            log_ble_packet(item)
        await task

    asyncio.run(runner())


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    main()