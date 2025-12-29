# This is a simple script to open a connection to an Atmotube device,
# collect data for a specified duration, and log the received packets

# Note: this script will only work with bluetooth turned on and an
# Atmotube device in range. Specifically mine, change the MAC address
# below to match your device.

from bleak import BleakClient, BleakScanner
from atmotube import SPS30Packet, StatusPacket, BME280Packet, SGPC3Packet
from atmotube import start_gatt_notifications, get_available_services
import asyncio
import logging

ATMOTUBE = "C2:2B:42:15:30:89"  # the mac address of my Atmotube


async def collect_data(mac, queue, collection_time):
    async def callback_queue(packet):
        await queue.put(packet)

    device = await BleakScanner.find_device_by_address(mac)
    if not device:
        raise Exception("Device not found")

    async with BleakClient(device) as client:
        if not client.is_connected:
            raise Exception("Failed to connect to device")
        packet_list = get_available_services(client)
        await start_gatt_notifications(client, callback_queue,
                                       packet_list=packet_list)
        await asyncio.sleep(collection_time)
        await queue.put(None)


def log_packet(packet):
    match packet:
        case StatusPacket():
            logging.info(f"{str(packet.date_time)} - Status Packet - "
                         f"Battery: {packet.battery_level}%, "
                         f"PM Sensor: {packet.pm_sensor_status}, "
                         f"Pre-heating: {packet.pre_heating}, "
                         f"Error: {packet.error_flag}")
        case SPS30Packet():
            logging.info(f"{str(packet.date_time)} - SPS30 Packet - "
                         f"PM1: {packet.pm1} µg/m³, "
                         f"PM2.5: {packet.pm2_5} µg/m³, "
                         f"PM4: {packet.pm4} µg/m³, "
                         f"PM10: {packet.pm10} µg/m³")
        case BME280Packet():
            logging.info(f"{str(packet.date_time)} - BME280 Packet - "
                         f"Humidity: {packet.humidity}%, "
                         f"Temperature: {packet.temperature}°C, "
                         f"Pressure: {packet.pressure} mbar")
        case SGPC3Packet():
            logging.info(f"{str(packet.date_time)} - SGPC3 Packet - "
                         f"TVOC: {packet.tvoc} ppb")
        case _:
            logging.info("Unknown packet type")


def main():
    mac = ATMOTUBE
    collection_time = 60  # seconds
    queue = asyncio.Queue()

    async def runner():
        collector = asyncio.create_task(
            collect_data(mac, queue, collection_time)
            )
        while True:
            item = await queue.get()
            if item is None:
                break
            log_packet(item)
        await collector

    asyncio.run(runner())


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    main()
