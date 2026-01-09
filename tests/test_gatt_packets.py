from atmotube import (
    InvalidByteData,
    AtmotubeProStatus,
    AtmotubeProSPS30,
    AtmotubeProBME280,
    AtmotubeProSGPC3
)
from datetime import datetime
from itertools import permutations

import pytest

# Known examples
datetime_obj = datetime(2024, 1, 1, 12, 0, 0)
example_data = [ (AtmotubeProStatus,
   {"valid_byte" : bytearray(b'Ad'),
    "alt_byte": bytearray(b'Ac'),
    "invalid_byte" : bytearray(b'A'),
    "str" : (f"AtmotubeProStatus(date_time={str(datetime_obj)}, "
            f"pm_sensor_status=True, "
            f"error_flag=False, bonding_flag=False, "
            f"charging=False, charging_timer=False, "
            f"pre_heating=True, battery_level=100%)")}),
    (AtmotubeProSPS30,
     {"valid_byte": bytearray(b'd\x00\x00\xb9\x00\x00J\x01\x00o\x00\x00'),
      "alt_byte": bytearray(b'e\x00\x00\xb9\x00\x00J\x01\x00o\x00\x00'),
      "invalid_byte": bytearray(b'd\x00\x00\xb9\x00\x00J\x01'),
      "str": (f"AtmotubeProSPS30(date_time={str(datetime_obj)}, "
              f"pm1=1.0µg/m³, pm2_5=1.85µg/m³, "
              f"pm10=3.3µg/m³, pm4=1.11µg/m³)")}),
    (AtmotubeProBME280,
     {"valid_byte": bytearray(b'\x0e\x17\x8ao\x01\x00\x1a\t'),
      "alt_byte": bytearray(b'\x0e\x17\x8ao\x01\x00\x1a\x0a'),
      "invalid_byte": bytearray(b'\x0e\x17\x8ao\x01'),
      "str": (f"AtmotubeProBME280(date_time={str(datetime_obj)}, "
              f"humidity=14%, temperature=23.3°C, "
              f"pressure=940.9mbar)")}),
    (AtmotubeProSGPC3,
     {"valid_byte": bytearray(b'\x02\x00\x00\x00'),
      "alt_byte": bytearray(b'\x03\x00\x00\x00'),
      "invalid_byte": bytearray(b'\x02\x00\x00'),
      "str": (f"AtmotubeProSGPC3(date_time={str(datetime_obj)}, "
              f"tvoc=0.002ppb)")}),
]

@pytest.mark.parametrize("packet_cls,data", example_data)
def test_status_packet(packet_cls,data):
    p1 = packet_cls(data['valid_byte'], date_time=datetime_obj)
    p2 = packet_cls(data['valid_byte'], date_time=datetime_obj)
    p3 = packet_cls(data['alt_byte'], date_time=datetime_obj)
    assert p1 == p2
    assert p1 != p3
    assert str(p1) == data['str']
    assert repr(p1) == data['str']
    with pytest.raises(InvalidByteData):
        packet_cls(data['invalid_byte'], date_time=datetime_obj)


def test_packet_inequality():
    packets = [packet_cls(data['valid_byte'], date_time=datetime_obj) 
               for packet_cls, data in example_data]
    for p1, p2 in permutations(packets, 2):
        match p2:
            case p1.__class__():
                assert p1 == p2
            case _:
                assert p1 != p2

def test_packet_inequality_different_datetime():
    for packet_cls, data in example_data:
        p1 = packet_cls(data['valid_byte'], date_time=datetime_obj)
        p2 = packet_cls(data['valid_byte'])
        assert p1 != p2