# PymoTube
[![LICENSE](https://img.shields.io/badge/license-MIT-lightgrey.svg)](https://github.com/aefarrell/PymoTube/blob/main/LICENSE) [![Tests](https://github.com/aefarrell/PymoTube/actions/workflows/python-package.yml/badge.svg)](https://github.com/aefarrell/PymoTube/actions/workflows/python-package.yml) [![codecov](https://codecov.io/gh/aefarrell/PymoTube/graph/badge.svg?token=E4C64QPOYH)](https://codecov.io/gh/aefarrell/PymoTube)

A simple package for retrieving data from an AtmoTube PRO via [bluetooth](https://support.atmotube.com/en/articles/10364981-bluetooth-api#h_150b16091e). Currently it is just a set of helper classes for taking bytearrays returned by an AtmoTube PRO and turning it into a basic struct. This package is intended to be used with [bleak](https://github.com/hbldh/bleak), a bluetooth library for Python. It does not handle connecting to the device or subscribing to notifications itself.

This package only supports the AtmoTube PRO device, and has only been tested with that device. I do not own any other AtmoTube devices, but reading the API documentation, I don't imagine they would work. I am open to extending this package to support other AtmoTube devices if someone with one of those devices would be willing to help test it. This package mostly exists so that you don't have to remember all the UUIDs and how to decode the bytearrays yourself.

There are two worked examples included in the `examples` directory, one for subscribing to GATT characteristics and one for listening to BLE advertisement and scan response packets. Both examples simply log the received packets to the console, but they can be easily extended to do something more useful, like storing it in a database or logging it to a csv.

## Installation

Pymotube is not available through pip yet, possibly ever, but you can install it directly from GitHub (bleeding edge):

```bash
git clone https://github.com/aefarrell/PymoTube.git
cd PymoTube
pip install .
```

Or you can download [the latest release](https://github.com/aefarrell/PymoTube/releases) and install it with pip:

```bash
pip install PymoTube-x.y.z.tar.gz
```

## Subscribing to GATT Characteristics

The simplest way to gather data from an Atmotube PRO is to subscribe to the GATT characteristics using the bluetooth library [bleak](https://github.com/hbldh/bleak). Pymotube provides some helper functions to make this easier.

### Finding available GATT Characteristics

You can use the `get_available_characteristics` function to generate a list of the GATT characteristics available from your AtmoTube PRO device, paired with the Pymotube class that can be used to decode the data.

```python
# with an existing connection to a BleakClient instance called client
from atmotube import get_available_characteristics

characteristics = get_available_characteristics(client)
for char_uuid, char_class in characteristics:
    print(f"Characteristic UUID: {char_uuid} can be decoded with class {char_class.__name__}")
```

Example output:
```
Characteristic UUID: DB450005-8E9A-4818-ADD7-6ED94A328AB4 can be decoded with class AtmotubeProSPS30
Characteristic UUID: DB450003-8E9A-4818-ADD7-6ED94A328AB4 can be decoded with class AtmotubeProBME280
Characteristic UUID: DB450002-8E9A-4818-ADD7-6ED94A328AB4 can be decoded with class AtmotubeProSGPC3
Characteristic UUID: DB450004-8E9A-4818-ADD7-6ED94A328AB4 can be decoded with class AtmotubeProStatus
```

### Subscribing to notifications

You can use the `start_gatt_notifications` function to subscribe to notifications for a given list of notifications (such as is returned by `get_available_characteristics`). You will need to provide a callback function which will be called with an instance of the appropriate class whenever new data is received.

```python
import asyncio
from bleak import BleakClient, BleakScanner
from atmotube import get_available_characteristics, start_gatt_notifications


def data_handler(packet):
    print(f"Received packet: {packet}")


async def main():
    device = await BleakScanner.find_device_by_address("C2:2B:42:15:30:89")  # Replace with your AtmoTube PRO MAC address
    async with BleakClient(device) as client:
        characteristics = get_available_characteristics(client)
        await start_gatt_notifications(client, data_handler, packet_list=characteristics)
        await asyncio.sleep(30.0)  # Listen for 30 seconds


asyncio.run(main())
```
Example output:
```
Received packet: AtmotubeProSGPC3(date_time=2026-01-10 18:06:04.218926, tvoc=0.075ppb)
Received packet: AtmotubeProBME280(date_time=2026-01-10 18:06:04.219090, humidity=28%, temperature=21.7°C, pressure=939.1mbar)
...
```

### The GATT Characteristic Data Classes

The following classes are used to decode the bytearrays returned by from the GATT characteristics for an AtmoTube PRO

#### Status Packet

The `StatusPacket` class takes a bytearray returned from the Status GATT characteristic and an optional datetime and creates a data structure with fields corresponding to the different status flags:

```python
from atmotube import StatusPacket
from datetime import datetime

example_date = datetime(2024, 1, 1, 12, 0, 0)
example_status = bytearray(b'Ad')
packet = StatusPacket(example_status, date_time=example_date)

print(packet)
```

```
StatusPacket(date_time=2024-01-01 12:00:00, pm_sensor_status=True, error_flag=False, bonding_flag=False, charging=False, charging_timer=False, pre_heating=True, battery_level=100%)
```

#### SPS30 Packet

The `SPS30Packet` takes a bytearray returned from the SPS30 GATT characteristic with an optional datetime and creates a data structure with fields corresponding to the PM measurements in ug/m^3

```python
from atmotube import SPS30Packet
from datetime import datetime

example_date = datetime(2024, 1, 1, 12, 0, 0)
example_sps30 = bytearray(b'd\x00\x00\xb9\x00\x00J\x01\x00o\x00\x00')
packet = SPS30Packet(example_sps30, date_time=example_date)

print(packet)
```

```
SPS30Packet(date_time=2024-01-01 12:00:00, pm1=1.0µg/m³, pm2_5=1.85µg/m³, pm10=3.3µg/m³, pm4=1.11µg/m³)
```

#### BME280 Packet

The `BME280Packet` takes a bytearray returned from the BME280 GATT characteristic with an optional datetime and creates a datastructure with fields corresponding the temperature, pressure, and humidity.

```python
from atmotube import BME280Packet
from datetime import datetime

example_date = datetime(2024, 1, 1, 12, 0, 0)
example_bme280 = bytearray(b'\x0e\x17\x8ao\x01\x00\x1a\t')
packet = BME280Packet(example_bme280, date_time=example_date)

print(packet)
```

```
BME280Packet(date_time=2024-01-01 12:00:00, humidity=14%, temperature=23.3°C, pressure=940.9mbar)
```

#### SGPC3 Packet

The `SGPC3Packet` takes a bytearray returned from the SGPC3 GATT characteristic with an optional datetime and creates a datastructure with a single field for the VOC.

```python
from atmotube import SGPC3Packet
from datetime import datetime

example_date = datetime(2024, 1, 1, 12, 0, 0)
example_sgpc3 = bytearray(b'\x02\x00\x00\x00')
packet = SGPC3Packet(example_sgpc3, date_time=example_date)

print(packet)
```

```
SGPC3Packet(date_time=2024-01-01 12:00:00, tvoc=0.002ppb)
```

## Listening for BLE advertisements and scan response packets

Pymotube also provides some helper functions for decoding BLE advertisement and scan response packets broadcast by the AtmoTube PRO. These can be used with bleak's `BleakScanner` to listen for packets without connecting to the device.

```python
import asyncio
from bleak import BleakScanner
from atmotube import ble_callback_wrapper

def data_handler(device, packet):
    print(f"Received a packet from {device.name}: {packet}")

async def main():
    ble_callback = ble_callback_wrapper(data_handler)
    async with BleakScanner(ble_callback):
        await asyncio.sleep(30.0)  # Listen for 30 seconds

asyncio.run(main())
```

Example output:
```
Received a packet from None: None
Received a packet from ATMOTUBE: AtmotubeProBLEScanResponse(date_time=2026-01-10 17:54:12.124663, pm1=1µg/m³, pm2_5=2µg/m³, pm10=3µg/m³, firmware_version=116.5.30)
Received a packet from None: None
Received a packet from ATMOTUBE: AtmotubeProBLEAdvertising(date_time=2026-01-10 17:54:14.302703, device_id=12863, tvoc=Noneppb, humidity=29%, temperature=22°C, pressure=939.32mbar, pm_sensor_status=True, error_flag=False, bonding_flag=False, charging=True, charging_timer=False, pre_heating=False, battery_level=99%)
```

Note that some packets may not be from an AtmoTube PRO device, in which case the device and packet will be `None`. Also note that the level of precision is less than what you get when subscribed to GATT notifications, this is especially notable for PM measurements which are given to the nearest integer value of ug/m^3.

### The BLE Advertisement and Scan Response Data Classes

The following classes are used to decode the bytearrays returned by from the BLE advertisement and scan response packets for an AtmoTube PRO

#### The BLE Advertising Packet

The `AtmotubeProBLEAdvertising` class takes a bytearray returned from a BLE advertisement packet and an optional datetime and creates a data structure with fields corresponding to the different measurements and status flags:

```python
from atmotube import AtmotubeProBLEAdvertising
from datetime import datetime

example_date = datetime(2024, 1, 1, 12, 0, 0)
example_advertising = bytearray(b'\x0052?\x16\x15\x00\x01i\x92Ac')
packet = AtmotubeProBLEAdvertising(example_advertising, date_time=example_date)

print(packet)
```

```
AtmotubeProBLEAdvertising(date_time=2024-01-01 12:00:00, device_id=12863, tvoc=0.053ppb, humidity=22%, temperature=21°C, pressure=925.62mbar, pm_sensor_status=True, error_flag=False, bonding_flag=False, charging=False, charging_timer=False, pre_heating=True, battery_level=99%)
```

#### The BLE Scan Response Packet

The `AtmotubeProBLEScanResponse` class takes a bytearray returned from a BLE scan response packet and an optional datetime and creates a data structure with fields corresponding to the different PM measurements and firmware version:

```python
from atmotube import AtmotubeProBLEScanResponse
from datetime import datetime

example_date = datetime(2024, 1, 1, 12, 0, 0)
example_scan_response = bytearray(b'\x00\x02\x00\x03\x00\x04t\x05\x1e')
packet = AtmotubeProBLEScanResponse(example_scan_response, date_time=example_date)

print(packet)
```

```
AtmotubeProBLEScanResponse(date_time=2024-01-01 12:00:00, pm1=2µg/m³, pm2_5=3µg/m³, pm10=4µg/m³, firmware_version=116.5.30)
```
