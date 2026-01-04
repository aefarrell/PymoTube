import pytest
from unittest.mock import ANY, AsyncMock, Mock
from bleak import BleakClient

from atmotube import (
    AtmoTube_Service_UUID,
    AtmoTube_PRO_UUID,
    StatusPacket,
    SPS30Packet,
    BME280Packet,
    SGPC3Packet,
    InvalidAtmoTubeService,
    get_available_characteristics,
    gatt_notify)

ALL_PACKETS = [(AtmoTube_PRO_UUID.STATUS, StatusPacket),
               (AtmoTube_PRO_UUID.SPS30, SPS30Packet),
               (AtmoTube_PRO_UUID.BME280, BME280Packet),
               (AtmoTube_PRO_UUID.SGPC3, SGPC3Packet)]


def test_get_available_characteristics_all():
    client = Mock(spec=BleakClient)
    client.services.get_service.return_value = Mock(
        uuid=AtmoTube_Service_UUID.PRO,
        characteristics=[
            Mock(uuid=AtmoTube_PRO_UUID.SGPC3),
            Mock(uuid=AtmoTube_PRO_UUID.BME280),
            Mock(uuid=AtmoTube_PRO_UUID.STATUS),
            Mock(uuid=AtmoTube_PRO_UUID.SPS30),
        ]
    )

    # Call the function
    packet_list = get_available_characteristics(client)

    # Assertions
    assert packet_list == ALL_PACKETS


def test_get_available_characteristics_no_pm():
    client = Mock(spec=BleakClient)
    client.services.get_service.return_value = Mock(
        uuid=AtmoTube_Service_UUID.PRO,
        characteristics=[
            Mock(uuid=AtmoTube_PRO_UUID.SGPC3),
            Mock(uuid=AtmoTube_PRO_UUID.BME280),
            Mock(uuid=AtmoTube_PRO_UUID.STATUS),
        ]
    )

    # Call the function
    packet_list = get_available_characteristics(client)

    # Assertions
    assert packet_list == [packet for packet in ALL_PACKETS
                           if packet[0] != AtmoTube_PRO_UUID.SPS30]


def test_get_available_characteristics_invalid_service():
    client = Mock(spec=BleakClient)
    client.services.get_service.return_value = None

    # Call the function and expect an exception
    try:
        get_available_characteristics(client)
    except Exception as e:
        assert isinstance(e, InvalidAtmoTubeService)
        assert str(e) == "AtmoTube Pro service not found"
    else:
        assert False, "Expected exception was not raised"


class MockPacket:
    def __init__(self, data):
        self.data = data


@pytest.mark.asyncio
async def test_gatt_notify_async_callback():
    uuid = "example-uuid"
    client = AsyncMock(spec=BleakClient)
    callback = AsyncMock()

    # Call gatt_notify, and await the returned task
    task = gatt_notify(client, uuid, MockPacket, callback)
    await task

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
