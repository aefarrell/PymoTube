from atmotube import (
    InvalidByteData,
    StatusPacket, SPS30Packet, BME280Packet, SGPC3Packet
)
from datetime import datetime

import pytest

# Status Packet tests
datetime_obj = datetime(2024, 1, 1, 12, 0, 0)
status_test_byte = bytearray(b'Ad')
status_test_invalid_byte = bytearray(b'A')
status_packet_str = (f"StatusPacket(date_time={str(datetime_obj)}, "
                     f"pm_sensor_status=True, "
                     f"error_flag=False, bonding_flag=False, "
                     f"charging=False, charging_timer=False, "
                     f"pre_heating=True, battery_level=100%)")


def test_status_packet():
    packet = StatusPacket(status_test_byte, date_time=datetime_obj)
    assert packet.pm_sensor_status is True
    assert packet.error_flag is False
    assert packet.bonding_flag is False
    assert packet.charging is False
    assert packet.charging_timer is False
    assert packet.pre_heating is True
    assert packet.battery_level == 100
    assert str(packet) == status_packet_str
    assert repr(packet) == status_packet_str
    with pytest.raises(InvalidByteData):
        StatusPacket(status_test_invalid_byte, date_time=datetime_obj)


# SPS30 Packet tests
sps30_test_byte = bytearray(b'd\x00\x00\xb9\x00\x00J\x01\x00o\x00\x00')
sps30_test_invalid_byte = bytearray(b'd\x00\x00\xb9\x00\x00J\x01')
sps30_test_str = (f"SPS30Packet(date_time={str(datetime_obj)}, "
                  f"pm1=1.0µg/m³, pm2_5=1.85µg/m³, "
                  f"pm10=3.3µg/m³, pm4=1.11µg/m³)")


def test_sps30_packet():
    packet = SPS30Packet(sps30_test_byte, date_time=datetime_obj)
    assert packet.pm1 == 1.0
    assert packet.pm2_5 == 1.85
    assert packet.pm10 == 3.3
    assert packet.pm4 == 1.11
    assert str(packet) == sps30_test_str
    assert repr(packet) == sps30_test_str
    with pytest.raises(InvalidByteData):
        SPS30Packet(sps30_test_invalid_byte, date_time=datetime_obj)


# BME280 Packet tests
bme280_test_byte = bytearray(b'\x0e\x17\x8ao\x01\x00\x1a\t')
bme280_test_invalid_byte = bytearray(b'\x0e\x17\x8ao\x01')
bme280_test_str = (f"BME280Packet(date_time={str(datetime_obj)}, "
                   f"humidity=14%, temperature=23.3°C, "
                   f"pressure=940.9mbar)")


def test_bme280_packet():
    packet = BME280Packet(bme280_test_byte, date_time=datetime_obj)
    assert packet.humidity == 14
    assert packet.temperature == 23.3
    assert packet.pressure == 940.9
    assert str(packet) == bme280_test_str
    assert repr(packet) == bme280_test_str
    with pytest.raises(InvalidByteData):
        BME280Packet(bme280_test_invalid_byte, date_time=datetime_obj)


# SGPC3 Packet tests
sgpc3_test_byte = bytearray(b'\x02\x00\x00\x00')
sgpc3_test_invalid_byte = bytearray(b'\x02\x00\x00')
sgpc3_test_str = (f"SGPC3Packet(date_time={str(datetime_obj)}, "
                  f"tvoc=0.002ppb)")


def test_sgpc3_packet():
    packet = SGPC3Packet(sgpc3_test_byte, date_time=datetime_obj)
    assert packet.tvoc == 0.002
    assert str(packet) == sgpc3_test_str
    assert repr(packet) == sgpc3_test_str
    with pytest.raises(InvalidByteData):
        SGPC3Packet(sgpc3_test_invalid_byte, date_time=datetime_obj)
