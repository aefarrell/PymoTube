from bleak import BleakClient, BleakGATTCharacteristic
from collections.abc import Callable, Awaitable
from typing import TypeAlias

import asyncio
import inspect

from .uuids import AtmoTube_Service_UUID, AtmoTube_PRO_UUID
from .packets import (
    AtmoTubePacket,
    StatusPacket, SPS30Packet, BME280Packet, SGPC3Packet)

PacketList: TypeAlias = list[tuple[AtmoTube_PRO_UUID, AtmoTubePacket]]

ALL_PACKETS = [(AtmoTube_PRO_UUID.STATUS, StatusPacket),
               (AtmoTube_PRO_UUID.SPS30, SPS30Packet),
               (AtmoTube_PRO_UUID.BME280, BME280Packet),
               (AtmoTube_PRO_UUID.SGPC3, SGPC3Packet)]


class InvalidAtmoTubeService(Exception):
    pass


def get_available_characteristics(client: BleakClient) -> PacketList:
    """
    Get the list of supported GATT characteristics on the connected Atmotube
    device.

    :param client: The BleakClient instance of the connected Atmotube device
    :type client: BleakClient
    :return: A list of tuples containing the UUIDs and packet classes
    :rtype: PacketList
    """
    srv = client.services.get_service(AtmoTube_Service_UUID.PRO)
    if not srv:
        raise InvalidAtmoTubeService("AtmoTube Pro service not found")
    characteristics = [char.uuid.lower() for char in srv.characteristics]
    return [(uuid, packet_cls)
            for uuid, packet_cls in ALL_PACKETS
            if uuid.lower() in characteristics]


def gatt_notify(client: BleakClient, uuid: str | AtmoTube_PRO_UUID,
                packet_cls: AtmoTubePacket,
                callback: Callable[[AtmoTubePacket], None]) -> Awaitable:
    """
    Start GATT notifications for a specific characteristic UUID.

    :param client: The BleakClient instance of the connected Atmotube device
    :type client: BleakClient
    :param uuid: The UUID of the characteristic to notify
    :type uuid: str | AtmoTube_PRO_UUID
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
