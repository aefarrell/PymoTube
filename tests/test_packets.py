from PymoTube import StatusPacket, SPS30Packet, BME280Packet, SGPC3Packet

status_test_byte = bytearray(b'Ad')
def test_status_packet():
    packet = StatusPacket(status_test_byte)
    assert packet.pm_sensor_status is True
    assert packet.error_flag is False
    assert packet.bonding_flag is False
    assert packet.charging is False
    assert packet.charging_timer is False
    assert packet.pre_heating is True
    assert packet.battery_level == 100

sps30_test_byte = bytearray(b'd\x00\x00\xb9\x00\x00J\x01\x00o\x00\x00')
def test_sps30_packet():
    packet = SPS30Packet(sps30_test_byte)
    assert packet.pm1 == 1.0
    assert packet.pm2_5 == 1.85
    assert packet.pm10 == 3.3
    assert packet.pm4 == 1.11

bme280_test_byte = bytearray(b'\x0e\x17\x8ao\x01\x00\x1a\t')
def test_bme280_packet():
    packet = BME280Packet(bme280_test_byte)
    assert packet.humidity == 14
    assert packet.temperature == 23.3
    assert packet.pressure == 940.9

sgpc3_test_byte = bytearray(b'\x02\x00\x00\x00')
def test_sgpc3_packet():
    packet = SGPC3Packet(sgpc3_test_byte)
    assert packet.tvoc == 0.002