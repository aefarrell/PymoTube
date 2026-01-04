from bleak import BleakClient, BleakGATTCharacteristic
from collections.abc import Callable, Awaitable
from typing import TypeAlias

import asyncio
import inspect

from .uuids import AtmotubeProService_UUID, AtmotubeProGATT_UUID
from .packets import (
    AtmotubePacket,
    AtmotubeProStatus, AtmotubeProSPS30, AtmotubeProBME280, AtmotubeProSGPC3)

PacketList: TypeAlias = list[tuple[AtmotubeProGATT_UUID, AtmotubePacket]]

ATMOTUBE_PRO_PACKETS = {AtmotubeProGATT_UUID.STATUS: AtmotubeProStatus,
                        AtmotubeProGATT_UUID.SPS30: AtmotubeProSPS30,
                        AtmotubeProGATT_UUID.BME280: AtmotubeProBME280,
                        AtmotubeProGATT_UUID.SGPC3: AtmotubeProSGPC3}


class InvalidAtmotubeService(Exception):
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
    srv = client.services.get_service(AtmotubeProService_UUID.PRO)
    if not srv:
        raise InvalidAtmotubeService("AtmoTube Pro service not found")
    characteristics = [char.uuid.upper() for char in srv.characteristics]
    return [(uuid, ATMOTUBE_PRO_PACKETS.get(uuid))
            for uuid in characteristics
            if uuid in ATMOTUBE_PRO_PACKETS.keys()]


def gatt_notify(client: BleakClient, uuid: str | AtmotubeProGATT_UUID,
                packet_cls: AtmotubePacket,
                callback: Callable[[AtmotubePacket], None]) -> Awaitable:
    """
    Start GATT notifications for a specific characteristic UUID.

    :param client: The BleakClient instance of the connected Atmotube device
    :type client: BleakClient
    :param uuid: The UUID of the characteristic to notify
    :type uuid: str | AtmotubeProGATT_UUID
    :param packet_cls: The packet class to instantiate from the received data
    :type packet_cls: AtmotubePacket
    :param callback: The callback function to call when a packet is received
    :type callback: Callable[[AtmotubePacket], None]
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
        callback: Callable[[AtmotubePacket], None],
        packet_list: PacketList = list(ATMOTUBE_PRO_PACKETS.items())) -> None:
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
