from abc import abstractmethod
from ctypes import (BigEndianStructure,
                    LittleEndianStructure,
                    c_ubyte,
                    c_byte,
                    c_short,
                    c_int)
from datetime import datetime
from typing import TypeAlias

FieldList: TypeAlias = list[tuple]


class InvalidByteData(Exception):
    pass


# This class is intended to be abstract. It is only exposed to the user to use
# as a type hint forfunctions that accept any Atmotube packet.
class AtmotubeGATTPacket(LittleEndianStructure):
    """
    Abstract base class for Atmotube data packets.
    """
    _byte_size_: int = 0  # To be defined in subclasses

    def __new__(cls, data: bytearray, date_time: datetime | None = None):
        if len(data) != cls._byte_size_:
            raise InvalidByteData(f"Expected {cls._byte_size_} bytes, "
                                  f"got {len(data)} bytes")
        return cls.from_buffer_copy(data)

    def __init__(self, data: bytearray, date_time: datetime | None = None):

        if date_time is None:
            date_time = datetime.now()
        self.date_time = date_time
        self._process_bytes()

    def __repr__(self) -> str:
        return str(self)

    @abstractmethod
    def __eq__(self, other: object) -> bool:
        ...

    @abstractmethod
    def __str__(self) -> str:
        ...

    @abstractmethod
    def _process_bytes(self) -> None:
        ...


class AtmotubeProStatus(AtmotubeGATTPacket):
    """
    Represents the status packet from an Atmotube device.
    """
    _fields_: FieldList = [
                ("_pm_sensor", c_ubyte, 1),
                ("_error", c_ubyte, 1),
                ("_bonding", c_ubyte, 1),
                ("_charging", c_ubyte, 1),
                ("_charging_timer", c_ubyte, 1),
                ("_bit_6",  c_ubyte, 1),
                ("_pre_heating", c_ubyte, 1),
                ("_bit_8", c_ubyte, 1),
                ("_battery", c_ubyte, 8),
    ]

    _byte_size_: int = 2

    def _process_bytes(self) -> None:
        self.pm_sensor_status = bool(self._pm_sensor)
        self.error_flag = bool(self._error)
        self.bonding_flag = bool(self._bonding)
        self.charging = bool(self._charging)
        self.charging_timer = bool(self._charging_timer)
        self.pre_heating = bool(self._pre_heating)
        self.battery_level = self._battery

    def __str__(self) -> str:
        return (f"AtmotubeProStatus(date_time={str(self.date_time)}, "
                f"pm_sensor_status={self.pm_sensor_status}, "
                f"error_flag={self.error_flag}, "
                f"bonding_flag={self.bonding_flag}, "
                f"charging={self.charging}, "
                f"charging_timer={self.charging_timer}, "
                f"pre_heating={self.pre_heating}, "
                f"battery_level={self.battery_level}%)")

    def __eq__(self, other: object) -> bool:
        if not isinstance(other, AtmotubeProStatus):
            return False
        return all((self.date_time == other.date_time,
                    self.pm_sensor_status == other.pm_sensor_status,
                    self.error_flag == other.error_flag,
                    self.bonding_flag == other.bonding_flag,
                    self.charging == other.charging,
                    self.charging_timer == other.charging_timer,
                    self.pre_heating == other.pre_heating,
                    self.battery_level == other.battery_level))


class AtmotubeProSPS30(AtmotubeGATTPacket):
    """
    Represents the SPS30 particulate matter sensor data packet from an
    Atmotube device.
    """
    _fields_: FieldList = [
        ('_pm1', c_byte*3),
        ('_pm2_5', c_byte*3),
        ('_pm10', c_byte*3),
        ('_pm4', c_byte*3),
    ]

    _pack_: bool = True
    _layout_: str = "ms"
    _byte_size_: int = 12

    def pm_from_bytes(self, byte_array: bytearray) -> float | None:
        res = int.from_bytes(byte_array, byteorder='little', signed=True)
        return res/100.0 if res > 0 else None

    def _process_bytes(self) -> None:
        self.pm1 = self.pm_from_bytes(self._pm1)
        self.pm2_5 = self.pm_from_bytes(self._pm2_5)
        self.pm10 = self.pm_from_bytes(self._pm10)
        self.pm4 = self.pm_from_bytes(self._pm4)

    def __str__(self) -> str:
        return (f"AtmotubeProSPS30(date_time={str(self.date_time)}, "
                f"pm1={self.pm1}µg/m³, pm2_5={self.pm2_5}µg/m³, "
                f"pm10={self.pm10}µg/m³, pm4={self.pm4}µg/m³)")

    def __eq__(self, other: object) -> bool:
        if not isinstance(other, AtmotubeProSPS30):
            return False
        return all((self.date_time == other.date_time,
                    self.pm1 == other.pm1,
                    self.pm2_5 == other.pm2_5,
                    self.pm10 == other.pm10,
                    self.pm4 == other.pm4))


class AtmotubeProBME280(AtmotubeGATTPacket):
    """
    Represents the BME280 environmental sensor data packet from an
    Atmotube device.
    """
    _fields_: FieldList = [
        ('_rh', c_byte),
        ('_T', c_byte),
        ('_P', c_int),
        ('_T_dec', c_short),
        ]

    _pack_: bool = True
    _layout_: str = "ms"
    _byte_size_: int = 8

    def _process_bytes(self) -> None:
        self.humidity = self._rh if self._rh > 0 else None
        self.temperature = self._T_dec / 100.0
        self.pressure = self._P / 100.0 if self._P > 0 else None

    def __str__(self) -> str:
        return (f"AtmotubeProBME280(date_time={str(self.date_time)}, "
                f"humidity={self.humidity}%, "
                f"temperature={self.temperature}°C, "
                f"pressure={self.pressure}mbar)")

    def __eq__(self, other: object) -> bool:
        if not isinstance(other, AtmotubeProBME280):
            return False
        return all((self.date_time == other.date_time,
                    self.humidity == other.humidity,
                    self.temperature == other.temperature,
                    self.pressure == other.pressure))


class AtmotubeProSGPC3(AtmotubeGATTPacket):
    """
    Represents the SGPC3 air quality sensor data packet from an
    Atmotube device.
    """
    _fields_: FieldList = [
        ('_tvoc', c_short)
    ]

    _pack_: bool = True
    _layout_: str = "ms"
    _byte_size_: int = 4

    def _process_bytes(self) -> None:
        self.tvoc = self._tvoc/1000.0 if self._tvoc > 0 else None

    def __str__(self) -> str:
        return (f"AtmotubeProSGPC3(date_time={str(self.date_time)}, "
                f"tvoc={self.tvoc}ppb)")

    def __eq__(self, other: object) -> bool:
        if not isinstance(other, AtmotubeProSGPC3):
            return False
        return all((self.date_time == other.date_time,
                    self.tvoc == other.tvoc))


class AtmotubeBLEPacket(BigEndianStructure):
    """
    Abstract base class for Atmotube data packets.
    """
    _byte_size_: int = 0  # To be defined in subclasses

    def __new__(cls, data: bytearray, date_time: datetime | None = None):
        if len(data) != cls._byte_size_:
            raise InvalidByteData(f"Expected {cls._byte_size_} bytes, "
                                  f"got {len(data)} bytes")
        return cls.from_buffer_copy(data)

    def __init__(self, data: bytearray, date_time: datetime | None = None):

        if date_time is None:
            date_time = datetime.now()
        self.date_time = date_time
        self._process_bytes()

    def __repr__(self) -> str:
        return str(self)

    @abstractmethod
    def __eq__(self, other: object) -> bool:
        ...

    @abstractmethod
    def __str__(self) -> str:
        ...

    @abstractmethod
    def _process_bytes(self) -> None:
        ...


class AtmotubeProBLEAdvertising(AtmotubeBLEPacket):
    """
    Represents the BLE advertising packet from an Atmotube PRO device.
    """
    _fields_: FieldList = [
        ('_tvoc', c_short, 16),
        ('_devid', c_short, 16),
        ('_rh', c_byte, 8),
        ('_T', c_byte, 8),
        ('_P', c_int, 32),
        ("_bit_8", c_ubyte, 1),
        ("_pre_heating", c_ubyte, 1),
        ("_bit_6",  c_ubyte, 1),
        ("_charging_timer", c_ubyte, 1),
        ("_charging", c_ubyte, 1),
        ("_bonding", c_ubyte, 1),
        ("_error", c_ubyte, 1),
        ("_pm_sensor", c_ubyte, 1),
        ("_battery", c_ubyte, 8),
    ]

    _pack_: bool = True
    _layout_: str = "ms"
    _byte_size_: int = 12

    def _process_bytes(self) -> None:
        self.tvoc = self._tvoc/1000.0 if self._tvoc > 0 else None
        self.device_id = self._devid
        self.humidity = self._rh if self._rh > 0 else None
        self.temperature = self._T
        self.pressure = self._P / 100.0 if self._P > 0 else None
        self.pm_sensor_status = bool(self._pm_sensor)
        self.error_flag = bool(self._error)
        self.bonding_flag = bool(self._bonding)
        self.charging = bool(self._charging)
        self.charging_timer = bool(self._charging_timer)
        self.pre_heating = bool(self._pre_heating)
        self.battery_level = self._battery

    def __str__(self) -> str:
        return (f"AtmotubeProBLEAdvertising(date_time={str(self.date_time)}, "
                f"device_id={self.device_id}, "
                f"tvoc={self.tvoc}ppb, "
                f"humidity={self.humidity}%, "
                f"temperature={self.temperature}°C, "
                f"pressure={self.pressure}mbar, "
                f"pm_sensor_status={self.pm_sensor_status}, "
                f"error_flag={self.error_flag}, "
                f"bonding_flag={self.bonding_flag}, "
                f"charging={self.charging}, "
                f"charging_timer={self.charging_timer}, "
                f"pre_heating={self.pre_heating}, "
                f"battery_level={self.battery_level}%)")

    def __eq__(self, other: object) -> bool:
        if not isinstance(other, AtmotubeProBLEAdvertising):
            return False
        return all((self.date_time == other.date_time,
                    self.device_id == other.device_id,
                    self.tvoc == other.tvoc,
                    self.humidity == other.humidity,
                    self.temperature == other.temperature,
                    self.pressure == other.pressure,
                    self.pm_sensor_status == other.pm_sensor_status,
                    self.error_flag == other.error_flag,
                    self.bonding_flag == other.bonding_flag,
                    self.charging == other.charging,
                    self.charging_timer == other.charging_timer,
                    self.pre_heating == other.pre_heating,
                    self.battery_level == other.battery_level))


class AtmotubeProBLEScanResponse(AtmotubeBLEPacket):
    """
    Represents the BLE scan response packet from an Atmotube PRO device.
    """
    _fields_: FieldList = [
        ('_pm1', c_short),
        ('_pm2_5', c_short),
        ('_pm10', c_short),
        ('_fw_maj', c_ubyte),
        ('_fw_min', c_ubyte),
        ('_fw_bld', c_ubyte),
    ]

    _pack_: bool = True
    _layout_: str = "ms"
    _byte_size_: int = 9

    def _process_bytes(self) -> None:
        self.pm1 = self._pm1 if self._pm1 > 0 else None
        self.pm2_5 = self._pm2_5 if self._pm2_5 > 0 else None
        self.pm10 = self._pm10 if self._pm10 > 0 else None
        self.firmware_version = f"{self._fw_maj}.{self._fw_min}.{self._fw_bld}"

    def __str__(self) -> str:
        return (f"AtmotubeProBLEScanResponse(date_time={str(self.date_time)}, "
                f"pm1={self.pm1}µg/m³, "
                f"pm2_5={self.pm2_5}µg/m³, "
                f"pm10={self.pm10}µg/m³, "
                f"firmware_version={self.firmware_version})")

    def __eq__(self, other: object) -> bool:
        if not isinstance(other, AtmotubeProBLEScanResponse):
            return False
        return all((self.date_time == other.date_time,
                    self.pm1 == other.pm1,
                    self.pm2_5 == other.pm2_5,
                    self.pm10 == other.pm10,
                    self.firmware_version == other.firmware_version))
