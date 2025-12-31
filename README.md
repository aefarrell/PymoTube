# PymoTube
[![LICENSE](https://img.shields.io/badge/license-MIT-lightgrey.svg)](https://github.com/aefarrell/PymoTube/blob/main/LICENSE) [![Tests](https://github.com/aefarrell/PymoTube/actions/workflows/python-package.yml/badge.svg)](https://github.com/aefarrell/PymoTube/actions/workflows/python-package.yml) [![codecov](https://codecov.io/gh/aefarrell/PymoTube/graph/badge.svg?token=E4C64QPOYH)](https://codecov.io/gh/aefarrell/PymoTube)

A simple package for retrieving data from an AtmoTube via bluetooth. Very much in development.

Currently it is just a set of helper classes for taking bytearrays returned by the AtmoTube and turning it into a basic struct.

## Packets

### Status Packet

The `StatusPacket` class takes a bytearray returned from the Status GATT characteristic and an optional datetime and creates a data structure with fields corresponding to the different status flags:

```python
from atmotube import StatusPacket
from datetime import datetime

example_date = datetime(2024, 1, 1, 12, 0, 0)
example_status = bytearray(b'Ad')
packet = StatusPacket(example_status, date_time=example_date)

print(packet)
# StatusPacket(date_time=2024-01-01 12:00:00, pm_sensor_status=True, error_flag=False, bonding_flag=False, charging=False, charging_timer=False, pre_heating=True, battery_level=100%)
```

### SPS30 Packet

The `SPS30Packet` takes a bytearray returned from the SPS30 GATT characteristic with an optional datetime and creates a data structure with fields corresponding to the PM measurements in ug/m^3

```python
from atmotube import SPS30Packet
from datetime import datetime

example_date = datetime(2024, 1, 1, 12, 0, 0)
example_sps30 = bytearray(b'd\x00\x00\xb9\x00\x00J\x01\x00o\x00\x00')
packet = SPS30Packet(example_sps30, date_time=example_date)

print(packet)
# SPS30Packet(date_time=2024-01-01 12:00:00, pm1=1.0µg/m³, pm2_5=1.85µg/m³, pm10=3.3µg/m³, pm4=1.11µg/m³)
```

### BME280 Packet

The `BME280Packet` takes a bytearray returned from the BME280 GATT characteristic with an optional datetime and creates a datastructure with fields corresponding the temperature, pressure, and humidity.

```python
from atmotube import BME280Packet
from datetime import datetime

example_date = datetime(2024, 1, 1, 12, 0, 0)
example_bme280 = bytearray(b'\x0e\x17\x8ao\x01\x00\x1a\t')
packet = BME280Packet(example_bme280, date_time=example_date)

print(packet)
# BME280Packet(date_time=2024-01-01 12:00:00, humidity=14%, temperature=23.3°C, pressure=940.9mbar)
```

### SGPC3 Packet

The `SGPC3Packet` takes a bytearray returned from the SGPC3 GATT characteristic with an optional datetime and creates a datastructure with a single field for the VOC.

```python
from atmotube import SGPC3Packet
from datetime import datetime

example_date = datetime(2024, 1, 1, 12, 0, 0)
example_sgpc3 = bytearray(b'\x02\x00\x00\x00')
packet = SGPC3Packet(example_sgpc3, date_time=example_date)

print(packet)
# SGPC3Packet(date_time=2024-01-01 12:00:00, tvoc=0.002ppb)
```
