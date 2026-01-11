import pytest
from unittest.mock import ANY, AsyncMock, Mock
from bleak import BLEDevice
from bleak.backends.scanner import AdvertisementData

import logging


from atmotube import (
    get_ble_packet,
    ble_callback_wrapper,
    AtmotubeProBLEAdvertising,
    AtmotubeProBLEScanResponse,
)
from atmotube.ble import AtmotubeProBLE_CONSTS

TEST_PACKETS = [
    (AtmotubeProBLEAdvertising,bytearray(b'\x0052?\x16\x15\x00\x01i\x92Ac')),
    (AtmotubeProBLEScanResponse,bytearray(b'\x00\x02\x00\x03\x00\x04t\x05\x1e')),
    (None, bytearray(b'\x00\x01\x02'))
]

@pytest.mark.parametrize("packet_cls,byte_array", TEST_PACKETS)
def test_get_ble_packet(packet_cls, byte_array):
    p1 = get_ble_packet(byte_array)
    if packet_cls is None:
        assert p1 is None
        return
    ts = p1.date_time
    p2 = packet_cls(byte_array, date_time=ts)
    assert p1 == p2


def test_ble_callback_wrapper_sync():
    mock_callback = Mock()
    wrapped = ble_callback_wrapper(mock_callback)

    device = Mock(spec=BLEDevice)
    adv_data = AdvertisementData(
        local_name="ATMOTUBE",
        manufacturer_data={
            AtmotubeProBLE_CONSTS.MANUFACTURER_DATA_ID: TEST_PACKETS[0][1]
        },
        service_data={},
        service_uuids=[],
        rssi=-60,
        tx_power=None,
        platform_data=[]
    )

    wrapped(device, adv_data)

    mock_callback.assert_called_once()
    called_device, called_packet = mock_callback.call_args[0]
    assert called_device == device
    assert isinstance(called_packet, AtmotubeProBLEAdvertising)


@pytest.mark.asyncio
async def test_ble_callback_wrapper_async():
    mock_callback = AsyncMock()
    wrapped = ble_callback_wrapper(mock_callback)

    device = Mock(spec=BLEDevice)
    adv_data = AdvertisementData(
        local_name="ATMOTUBE",
        manufacturer_data={
            AtmotubeProBLE_CONSTS.MANUFACTURER_DATA_ID: TEST_PACKETS[1][1]
        },
        service_data={},
        service_uuids=[],
        rssi=-60,
        tx_power=None,
        platform_data=[]
    )

    await wrapped(device, adv_data)

    mock_callback.assert_awaited_once()
    called_device, called_packet = mock_callback.call_args[0]
    assert called_device == device
    assert isinstance(called_packet, AtmotubeProBLEScanResponse)