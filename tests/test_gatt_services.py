import pytest
from unittest.mock import ANY, AsyncMock, Mock
from bleak import BleakClient
from bleak.exc import BleakCharacteristicNotFoundError

from atmotube import (
    AtmotubeProService_UUID,
    AtmotubeProGATT_UUID,
    AtmotubeProStatus,
    AtmotubeProSPS30,
    AtmotubeProBME280,
    AtmotubeProSGPC3,
    InvalidAtmotubeService,
    get_available_characteristics,
    gatt_notify,
    start_gatt_notifications)

ALL_PACKETS = [(AtmotubeProGATT_UUID.STATUS, AtmotubeProStatus),
               (AtmotubeProGATT_UUID.SPS30, AtmotubeProSPS30),
               (AtmotubeProGATT_UUID.BME280, AtmotubeProBME280),
               (AtmotubeProGATT_UUID.SGPC3, AtmotubeProSGPC3)]

TEST_PACKETS = {AtmotubeProGATT_UUID.STATUS: bytearray(b'Ad'),
                AtmotubeProGATT_UUID.SPS30: bytearray(b'd\x00\x00\xb9\x00\x00J\x01\x00o\x00\x00'),
                AtmotubeProGATT_UUID.BME280: bytearray(b'\x0e\x17\x8ao\x01\x00\x1a\t'),
                AtmotubeProGATT_UUID.SGPC3: bytearray(b'\x02\x00\x00\x00')}


@pytest.mark.parametrize("uuid_list,packet_list", [
    ([uuid for uuid, _ in ALL_PACKETS], ALL_PACKETS),
    ([uuid for uuid, _ in ALL_PACKETS if uuid != AtmotubeProGATT_UUID.SPS30],
     [(u, p) for u, p in ALL_PACKETS if u != AtmotubeProGATT_UUID.SPS30]),
    ([], []),
    ([uuid for uuid, _ in ALL_PACKETS]+
     ["00001234-0000-1000-8000-00805f9b34fb"],
     ALL_PACKETS)
    ])
def test_get_available_characteristics(uuid_list, packet_list):
    # Mock BleakClient
    client = Mock(spec=BleakClient)
    client.services.get_service.return_value = Mock(
        uuid=AtmotubeProService_UUID.PRO,
        characteristics=[Mock(uuid=uuid) for uuid in uuid_list]
    )
    # Call the function
    returned_list = get_available_characteristics(client)

    # Assertions
    assert len(returned_list) == len(packet_list)
    assert set(returned_list) == set(packet_list)


def test_get_available_characteristics_invalid_service():
    client = Mock(spec=BleakClient)
    client.services.get_service.return_value = None
    with pytest.raises(InvalidAtmotubeService):
        get_available_characteristics(client)


class MockPacket:
    def __init__(self, data):
        self.data = data


@pytest.mark.asyncio
async def test_gatt_notify_async_callback():
    uuid = "example-uuid"
    client = AsyncMock(spec=BleakClient)
    callback = AsyncMock()

    # Call gatt_notify, and await the returned task
    await gatt_notify(client, uuid, MockPacket, callback)

    # Assert that start_notify was called with the uuid and something tbd
    client.start_notify.assert_called_once_with(uuid, ANY)

    # Dummy notification being sent
    packet_callback = client.start_notify.call_args[0][1]
    notification_data = bytearray([0, 1, 2, 3])
    await packet_callback(None, notification_data)

    # Assert that the original callback is called with one argument
    # and that argument is of the correct instance and holds the data
    callback.assert_awaited_once()
    callback.assert_called_once_with(ANY)
    assert isinstance(callback.call_args.args[0], MockPacket)
    assert callback.call_args.args[0].data == notification_data


@pytest.mark.asyncio
async def test_gatt_notify_concurrent_callback():
    uuid = "example-uuid"
    client = AsyncMock(spec=BleakClient)
    callback = Mock()

    # Call gatt_notify, and await the returned task
    await gatt_notify(client, uuid, MockPacket, callback)

    # Assert that start_notify was called with the uuid and something tbd
    client.start_notify.assert_called_once_with(uuid, ANY)

    # Dummy notification being sent
    packet_callback = client.start_notify.call_args[0][1]
    notification_data = bytearray([0, 1, 2, 3])
    packet_callback(None, notification_data)

    # Assert that the original callback is called with one argument
    # and that argument is of the correct instance and holds the data
    callback.assert_called_once_with(ANY)
    assert isinstance(callback.call_args.args[0], MockPacket)
    assert callback.call_args.args[0].data == notification_data


@pytest.mark.asyncio
async def test_gatt_notify_start_notify_failure():
    uuid = '00001234-0000-1000-8000-00805f9b34fb'
    client = AsyncMock(spec=BleakClient)
    client.start_notify.side_effect = BleakCharacteristicNotFoundError(f"Characteristic {uuid} was not found!")
    callback = Mock()

    # Call gatt_notify, and await the returned task
    with pytest.raises(BleakCharacteristicNotFoundError):
        await gatt_notify(client, uuid, MockPacket, callback)


@pytest.mark.asyncio
async def test_start_gatt_notifications():
    client = AsyncMock(spec=BleakClient)
    callback = Mock()

    packet_list = [(uuid, MockPacket) for uuid, _ in ALL_PACKETS]

    # Call start_gatt_notifications, and await the returned task
    await start_gatt_notifications(client, callback, packet_list)

    # Assert that start_notify was called with the correct UUIDs
    for call in client.start_notify.mock_calls:
        uuid, _ = call.args
        assert uuid in [packet[0] for packet in ALL_PACKETS]

    # Dummy notifications being sent
    for call in client.start_notify.mock_calls:
        uuid, packet_callback = call.args
        byte_data = TEST_PACKETS[uuid]
        packet_callback(None, (uuid, byte_data))

    # Assert that the original callback is called with correct packets
    for call in callback.mock_calls:
        packet = call.args[0]
        assert isinstance(packet, MockPacket)
        assert packet.data[1] == TEST_PACKETS[packet.data[0]]
