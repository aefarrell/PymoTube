from abc import abstractmethod
from ctypes import LittleEndianStructure, c_ubyte, c_byte, c_short, c_int
from datetime import datetime
from typing import TypeAlias

FieldList: TypeAlias = list[tuple]


class InvalidByteData(Exception):
    pass


# I have no idea how to make this actually an abstract sub-class of
# LittleEndianStructure so be mindful that this class is intended to be
# abstract. It is only exposed to the user to use as a type hint for
# functions that accept any Atmotube packet.
class AtmoTubePacket(LittleEndianStructure):
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
    def __str__(self) -> str:
        ...

    @abstractmethod
    def _process_bytes(self) -> None:
        ...


class StatusPacket(AtmoTubePacket):
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
        return (f"StatusPacket(date_time={str(self.date_time)}, "
                f"pm_sensor_status={self.pm_sensor_status}, "
                f"error_flag={self.error_flag}, "
                f"bonding_flag={self.bonding_flag}, "
                f"charging={self.charging}, "
                f"charging_timer={self.charging_timer}, "
                f"pre_heating={self.pre_heating}, "
                f"battery_level={self.battery_level}%)")


class SPS30Packet(AtmoTubePacket):
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

    _pack_: int = 1
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
        return (f"SPS30Packet(date_time={str(self.date_time)}, "
                f"pm1={self.pm1}µg/m³, pm2_5={self.pm2_5}µg/m³, "
                f"pm10={self.pm10}µg/m³, pm4={self.pm4}µg/m³)")


class BME280Packet(AtmoTubePacket):
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

    _pack_: int = 1
    _layout_: str = "ms"
    _byte_size_: int = 8

    def _process_bytes(self) -> None:
        self.humidity = self._rh if self._rh > 0 else None
        self.temperature = self._T_dec / 100.0
        self.pressure = self._P / 100.0 if self._P > 0 else None

    def __str__(self) -> str:
        return (f"BME280Packet(date_time={str(self.date_time)}, "
                f"humidity={self.humidity}%, "
                f"temperature={self.temperature}°C, "
                f"pressure={self.pressure}mbar)")


class SGPC3Packet(AtmoTubePacket):
    """
    Represents the SGPC3 air quality sensor data packet from an
    Atmotube device.
    """
    _fields_: FieldList = [
        ('_tvoc', c_short)
    ]

    _pack_: int = 1
    _layout_: str = "ms"
    _byte_size_: int = 4

    def _process_bytes(self) -> None:
        self.tvoc = self._tvoc/1000.0 if self._tvoc > 0 else None

    def __str__(self) -> str:
        return (f"SGPC3Packet(date_time={str(self.date_time)}, "
                f"tvoc={self.tvoc}ppb)")
