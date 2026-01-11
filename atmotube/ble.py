from enum import IntEnum
from bleak import BLEDevice
from bleak.backends.scanner import AdvertisementData

from .packets import (AtmotubeBLEPacket,
                      AtmotubeProBLEAdvertising,
                      AtmotubeProBLEScanResponse)

import inspect


class AtmotubeProBLE_CONSTS(IntEnum):
    MANUFACTURER_DATA_ID = int(0xFFFF)
    ADVERTISING_BYTE_LENGTH = 12
    SCAN_RESPONSE_BYTE_LENGTH = 9


PACKET_MAP = {
    AtmotubeProBLE_CONSTS.ADVERTISING_BYTE_LENGTH: AtmotubeProBLEAdvertising,
    AtmotubeProBLE_CONSTS.SCAN_RESPONSE_BYTE_LENGTH: AtmotubeProBLEScanResponse
}


def get_ble_packet(b: bytearray) -> AtmotubeBLEPacket | None:
    packet_cls = PACKET_MAP.get(len(b), None)
    if packet_cls:
        return packet_cls(b)
    else:
        return None


def ble_callback_wrapper(callback):
    if inspect.iscoroutinefunction(callback):
        async def wrapped_callback(device: BLEDevice,
                                   adv: AdvertisementData) -> None:
            mfr_data = adv.manufacturer_data.get(
                        AtmotubeProBLE_CONSTS.MANUFACTURER_DATA_ID,
                        bytearray(b''))
            packet = get_ble_packet(mfr_data)
            await callback(device, packet)
    else:
        def wrapped_callback(device: BLEDevice,
                             adv: AdvertisementData) -> None:
            mfr_data = adv.manufacturer_data.get(
                        AtmotubeProBLE_CONSTS.MANUFACTURER_DATA_ID,
                        bytearray(b''))
            packet = get_ble_packet(mfr_data)
            callback(device, packet)

    return wrapped_callback
