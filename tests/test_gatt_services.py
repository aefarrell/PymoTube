from unittest.mock import Mock, patch

from atmotube import (
    AtmoTube_Service_UUID,
    AtmoTube_PRO_UUID,
    InvalidAtmoTubeService,
    get_available_characteristics)

from atmotube.gatt_notify import ALL_PACKETS


def test_get_available_characteristics_all():
    with patch("bleak.BleakClient", new_callable=Mock) as MockClient:
        mock_client = MockClient.return_value
        mock_client.services.get_service.return_value = Mock(
            uuid=AtmoTube_Service_UUID.PRO,
            characteristics=[
                Mock(uuid=AtmoTube_PRO_UUID.SGPC3),
                Mock(uuid=AtmoTube_PRO_UUID.BME280),
                Mock(uuid=AtmoTube_PRO_UUID.STATUS),
                Mock(uuid=AtmoTube_PRO_UUID.SPS30),
            ]
        )

        # Call the function
        packet_list = get_available_characteristics(mock_client)

        # Assertions
        assert packet_list == ALL_PACKETS


def test_get_available_characteristics_no_pm():
    with patch("bleak.BleakClient", new_callable=Mock) as MockClient:
        mock_client = MockClient.return_value
        mock_client.services.get_service.return_value = Mock(
            uuid=AtmoTube_Service_UUID.PRO,
            characteristics=[
                Mock(uuid=AtmoTube_PRO_UUID.SGPC3),
                Mock(uuid=AtmoTube_PRO_UUID.BME280),
                Mock(uuid=AtmoTube_PRO_UUID.STATUS),
            ]
        )

        # Call the function
        packet_list = get_available_characteristics(mock_client)

        # Assertions
        assert packet_list == [packet for packet in ALL_PACKETS
                               if packet[0] != AtmoTube_PRO_UUID.SPS30]


def test_get_available_characteristics_invalid_service():
    with patch("bleak.BleakClient", new_callable=Mock) as MockClient:
        mock_client = MockClient.return_value
        mock_client.services.get_service.return_value = None

        # Call the function and expect an exception
        try:
            get_available_characteristics(mock_client)
        except Exception as e:
            assert isinstance(e, InvalidAtmoTubeService)
            assert str(e) == "AtmoTube Pro service not found"
        else:
            assert False, "Expected exception was not raised"
