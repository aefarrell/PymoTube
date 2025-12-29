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
    characteristics = [d.characteristic_uuid
                       for c in client.services.characteristics.values()
                       for d in c.descriptors]
    return [(uuid, packet_cls)
            for uuid, packet_cls in ALL_PACKETS
            if uuid.lower() in characteristics]


def gatt_notify(client: BleakClient, uuid: str | AtmoTube_GATT_UUID,
                packet_cls: AtmoTubePacket,
                callback: Callable[[AtmoTubePacket], None]) -> Awaitable:
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
    await asyncio.gather(*[gatt_notify(client, uuid, packet_cls, callback)
                           for uuid, packet_cls in packet_list])
