# This is a simple script to open a connection to an Atmotube device,
# collect data for a specified duration, and log the received packets

# Note: this script will only work with bluetooth turned on and an
# Atmotube device in range. Specifically mine, change the MAC address
# below to match your device.

from bleak import BleakClient, BleakScanner
from PymoTube import SPS30Packet, StatusPacket, BME280Packet, SGPC3Packet
from PymoTube.uuids import SPS30_UUID, STATUS_UUID, BME280_UUID, SGPC3_UUID
import asyncio, logging, time

ATMOTUBE = "C2:2B:42:15:30:89" # the mac address of my Atmotube

async def collect_data(mac, queue, collection_time):
    async def status_cb(char, data):
        status_packet = StatusPacket(data)
        await queue.put(status_packet)

    async def sps30_cb(char, data):
        sps30_packet = SPS30Packet(data)
        await queue.put(sps30_packet)
        
    async def bme280_cb(char, data):
        bme280_packet = BME280Packet(data)
        await queue.put(bme280_packet)

    async def sgp30_cb(char, data):
        sgp30_packet = SGPC3Packet(data)
        await queue.put(sgp30_packet)

    device = await BleakScanner.find_device_by_address(mac)
    if not device:
        raise Exception("Device not found")
    
    async with BleakClient(device) as client:
        await client.start_notify(SPS30_UUID, sps30_cb)
        await client.start_notify(STATUS_UUID, status_cb)
        await client.start_notify(BME280_UUID, bme280_cb)
        await client.start_notify(SGPC3_UUID, sgp30_cb)
        await asyncio.sleep(collection_time)
        await queue.put(None)

def log_packet(packet):
    match packet:
        case StatusPacket():
            logging.info(f"{time.ctime(packet.timestamp)} - Status Packet - Battery: {packet.battery_level}%, Charging: {packet.charging}, Error: {packet.error_flag}")
        case SPS30Packet():
            logging.info(f"{time.ctime(packet.timestamp)} - SPS30 Packet - PM1: {packet.pm1} µg/m³, PM2.5: {packet.pm2_5} µg/m³, PM4: {packet.pm4} µg/m³, PM10: {packet.pm10} µg/m³")
        case BME280Packet():
            logging.info(f"{time.ctime(packet.timestamp)} - BME280 Packet - Humidity: {packet.humidity}%, Temperature: {packet.temperature}°C, Pressure: {packet.pressure} mBar")
        case SGPC3Packet():
            logging.info(f"{time.ctime(packet.timestamp)} - SGPC3 Packet - TVOC: {packet.tvoc} ppb")
        case _:
            logging.info("Unknown packet type")

def main():
    mac = ATMOTUBE
    collection_time = 60  # seconds
    queue = asyncio.Queue()

    async def runner():
        collector = asyncio.create_task(collect_data(mac, queue, collection_time))
        while True:
            item = await queue.get()
            if item is None:
                break
            log_packet(item)
        await collector

    asyncio.run(runner())

if __name__ == "__main__":
    logger = logging.getLogger()
    logger.setLevel(logging.INFO)
    main()
