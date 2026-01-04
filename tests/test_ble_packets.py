from atmotube import (
    InvalidByteData,
    AtmotubeProBLEAdvertising,
    AtmotubeProBLEScanResponse
)
from datetime import datetime

import pytest

datetime_obj = datetime(2024, 1, 1, 12, 0, 0)
ble_adv_byte = bytearray(b'\x0052?\x16\x15\x00\x01i\x92Ac')
ble_adv_str = (f"AtmotubeProBLEAdvertising("
               f"date_time={str(datetime_obj)}, "
               f"device_id=12863, tvoc=0.053ppb, humidity=22%, "
               f"temperature=21°C, pressure=925.62mbar, "
               f"pm_sensor_status=True, error_flag=False, "
               f"bonding_flag=False, charging=False, "
               f"charging_timer=False, pre_heating=True, "
               f"battery_level=99%)")


def test_ble_advertising_packet():
    test = AtmotubeProBLEAdvertising(ble_adv_byte, date_time=datetime_obj)
    test2 = AtmotubeProBLEAdvertising(ble_adv_byte, date_time=datetime_obj)
    test3 = AtmotubeProBLEAdvertising(bytearray(b'\x0052?\x16\x15\x00\x01i\x93Ac'),
                                     date_time=datetime_obj)
    assert test == test2
    assert test != test3
    assert test.device_id == 12863
    assert test.tvoc == 0.053
    assert test.humidity == 22
    assert test.temperature == 21
    assert test.pressure == 925.62
    assert test.pm_sensor_status is True
    assert test.error_flag is False
    assert test.bonding_flag is False
    assert test.charging is False
    assert test.charging_timer is False
    assert test.pre_heating is True
    assert test.battery_level == 99
    assert str(test) == ble_adv_str
    assert repr(test) == ble_adv_str
    with pytest.raises(InvalidByteData):
        AtmotubeProBLEAdvertising(bytearray(b'\x0052?\x16\x15\x00\x01iA'))
    

ble_scn_byte = bytearray(b'\x00\x02\x00\x03\x00\x04t\x05\x1e')
ble_scn_str = (f"AtmotubeProBLEScanResponse(date_time={str(datetime_obj)}, "
               f"pm1=2µg/m³, pm2_5=3µg/m³, pm10=4µg/m³, "
               f"firmware_version=116.5.30)")


def test_ble_scan_response_packet():
    test = AtmotubeProBLEScanResponse(ble_scn_byte, date_time=datetime_obj)
    test2 = AtmotubeProBLEScanResponse(ble_scn_byte, date_time=datetime_obj)
    test3 = AtmotubeProBLEScanResponse(bytearray(b'\x00\x02\x00\x03\x00\x05t\x05\x1e'),
                                      date_time=datetime_obj)
    assert test == test2
    assert test != test3
    assert test.pm1 == 2
    assert test.pm2_5 == 3
    assert test.pm10 == 4
    assert test.firmware_version == "116.5.30"
    assert str(test) == ble_scn_str
    assert repr(test) == ble_scn_str
    with pytest.raises(InvalidByteData):
        AtmotubeProBLEScanResponse(bytearray(b'\x00\x02\x00\x03\x00\x04t\x05'), date_time=datetime_obj)

def test_ble_packets_inequality():
    adv_packet = AtmotubeProBLEAdvertising(ble_adv_byte, date_time=datetime_obj)
    scn_packet = AtmotubeProBLEScanResponse(ble_scn_byte, date_time=datetime_obj)
    assert adv_packet != scn_packet
    assert scn_packet != adv_packet