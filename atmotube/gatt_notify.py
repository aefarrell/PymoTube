from .uuids import AtmoTube_GATT_UUID
from .packets import AtmoTubePacket
from .packets import StatusPacket, SPS30Packet, BME280Packet, SGPC3Packet
from bleak import BleakClient, BleakGATTCharacteristic
from collections.abc import Callable, Awaitable
from typing import TypeAlias

import asyncio
import inspect

PacketList: TypeAlias = list[tuple[AtmoTube_GATT_UUID, AtmoTubePacket]]

ALL_PACKETS = [(AtmoTube_GATT_UUID.STATUS, StatusPacket),
               (AtmoTube_GATT_UUID.SPS30, SPS30Packet),
               (AtmoTube_GATT_UUID.BME280, BME280Packet),
               (AtmoTube_GATT_UUID.SGPC3, SGPC3Packet)]


def get_available_services(client: BleakClient) -> PacketList:
    """
    Get the list of supported services on the connected Atmotube device.

    :param client: The BleakClient instance of the connected Atmotube device
    :type client: BleakClient
    :return: A list of tuples containing the UUIDs and packet classes
    :rtype: PacketList
    """
    characteristics = [d.characteristic_uuid
                       for c in client.services.characteristics.values()
                       for d in c.descriptors]
    return [(uuid, packet_cls)
            for uuid, packet_cls in ALL_PACKETS
            if uuid.lower() in characteristics]


def gatt_notify(client: BleakClient, uuid: str | AtmoTube_GATT_UUID,
                packet_cls: AtmoTubePacket,
                callback: Callable[[AtmoTubePacket], None]) -> Awaitable:
    """
    Start GATT notifications for a specific characteristic UUID.

    :param client: The BleakClient instance of the connected Atmotube device
    :type client: BleakClient
    :param uuid: The UUID of the characteristic to notify
    :type uuid: str | AtmoTube_GATT_UUID
    :param packet_cls: The packet class to instantiate from the received data
    :type packet_cls: AtmoTubePacket
    :param callback: The callback function to call when a packet is received
    :type callback: Callable[[AtmoTubePacket], None]
    :return: An awaitable object representing the notification task
    :rtype: Awaitable
    """
    if inspect.iscoroutinefunction(callback):
        async def packet_callback(char: BleakGATTCharacteristic,
                                  data: bytearray):
            packet = packet_cls(data)
            await callback(packet)
    else:
        def packet_callback(char: BleakGATTCharacteristic,
                            data: bytearray):
            packet = packet_cls(data)
            callback(packet)

    return client.start_notify(uuid, packet_callback)


async def start_gatt_notifications(
        client: BleakClient,
        callback: Callable[[AtmoTubePacket], None],
        packet_list: PacketList = ALL_PACKETS) -> None:
    """
    Start GATT notifications for all specified characteristics.

    :param client: The BleakClient instance of the connected Atmotube device
    :type client: BleakClient
    :param callback: The callback function to call when a packet is received
    :type callback: Callable[[AtmoTubePacket], None]
    :param packet_list: The list of UUIDs and packet classes to notify
    :type packet_list: PacketList
    """
    await asyncio.gather(*[gatt_notify(client, uuid, packet_cls, callback)
                           for uuid, packet_cls in packet_list])
