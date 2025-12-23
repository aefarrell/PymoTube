# PymoTube
A simple API for retrieving data from an AtmoTube via bluetooth. Very much in development.

Currently it is just a set of helper classes for taking bytearrays returned by the AtmoTube and turning it into a basic struct.

## Packets

### Status Packet

The `StatusPacket` class takes a bytearray returned from the Status GATT characteristic and an optional timestamp and creates a data structure with fields corresponding to the different status flags:

```python
example_status = bytearray(b'Ad')
packet = StatusPacket(example_status)

# packet.pm_sensor_status : bool - whether the pm sensor is on
# packet.error_flag : bool - presence of an error code
# packet.bonding_flag : bool - bonding status, true is bonded
# packet.charging : bool - whether the device is current charging
# packet.charging_timer : bool - true: usb power was connected <30 min. ago
# packet.pre_heating : bool - false: SGPC3 device is pre-heating, true: SGPC3 device is ready
# packet.battery_level : int - battery level (percent)
```

### SPS30 Packet

The `SPS30Packet` takes a bytearray returned from the SPS30 GATT characteristic with an optional timestamp and creates a data structure with fields corresponding to the PM measurements in ug/m^3

```python
example_sps30 = bytearray(b'd\x00\x00\xb9\x00\x00J\x01\x00o\x00\x00')
packet = SPS30Packet(example_sps30)

# packet.pm1 : float   - particulat matter <1um 
# packet.pm2_5 : float - particulat matter <2.5um
# packet.pm4 : float   - particulat matter <4um 
# packet.pm10 : float  - particulat matter <10um
```

### BME280 Packet

The `BME280Packet` takes a bytearray returned from the BME280 GATT characteristic with an optional timestamp and creates a datastructure with fields corresponding the temperature, pressure, and humidity.

```python
example_bme280 = bytearray(b'\x0e\x17\x8ao\x01\x00\x1a\t')
packet = BME280Packet(example_bme280)

# packet.humidity : float    - relative humidity (%)
# packet.temperature : float - temperature (C)
# packet.pressure : float    - pressure (mbar) 
```

### SGPC3 Packet

The `SGPC3Packet` takes a bytearray returned from the SGPC3 GATT characteristic with an optional timestamp and creates a datastructure with a single field for the VOC.

```python
example_sgpc3 = bytearray(b'\x02\x00\x00\x00')
packet = SGPC3Packet(example_sgpc3)

# packet.tvoc : float - the total VOC in ppm
```
