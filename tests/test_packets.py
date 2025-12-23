from atmotube import StatusPacket, SPS30Packet, BME280Packet, SGPC3Packet

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
    assert str(packet) == "StatusPacket(pm_sensor_status=True, error_flag=False, bonding_flag=False, charging=False, charging_timer=False, pre_heating=True, battery_level=100%)"

sps30_test_byte = bytearray(b'd\x00\x00\xb9\x00\x00J\x01\x00o\x00\x00')
def test_sps30_packet():
    packet = SPS30Packet(sps30_test_byte)
    assert packet.pm1 == 1.0
    assert packet.pm2_5 == 1.85
    assert packet.pm10 == 3.3
    assert packet.pm4 == 1.11
    assert str(packet) == "SPS30Packet(pm1=1.0µg/m³, pm2_5=1.85µg/m³, pm10=3.3µg/m³, pm4=1.11µg/m³)"

bme280_test_byte = bytearray(b'\x0e\x17\x8ao\x01\x00\x1a\t')
def test_bme280_packet():
    packet = BME280Packet(bme280_test_byte)
    assert packet.humidity == 14
    assert packet.temperature == 23.3
    assert packet.pressure == 940.9
    assert str(packet) == "BME280Packet(humidity=14%, temperature=23.3°C, pressure=940.9mbar)"

sgpc3_test_byte = bytearray(b'\x02\x00\x00\x00')
def test_sgpc3_packet():
    packet = SGPC3Packet(sgpc3_test_byte)
    assert packet.tvoc == 0.002
    assert str(packet) == "SGPC3Packet(tvoc=0.002ppb)"