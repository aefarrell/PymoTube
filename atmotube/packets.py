from ctypes import LittleEndianStructure, c_ubyte, c_byte, c_short, c_int
import time


class InvalidByteData(Exception):
    pass


class AtmoTubePacket(LittleEndianStructure):
    _byte_size_ = 0  # To be defined in subclasses

    def __new__(cls, data, ts=None):
        if len(data) != cls._byte_size_:
            raise InvalidByteData(f"Expected {cls._byte_size_} bytes, "
                                  f"got {len(data)} bytes")
        return cls.from_buffer_copy(data)

    def __init__(self, data, ts=None):
        if ts is None:
            ts = time.time()
        self.timestamp = ts
        self._process_bytes()

    def __repr__(self):
        return str(self)

    def _process_bytes(self):
        ...


class StatusPacket(AtmoTubePacket):
    _fields_ = [
                ("_pm_sensor",          c_ubyte, 1),
                ("_error",              c_ubyte, 1),
                ("_bonding",            c_ubyte, 1),
                ("_charging",           c_ubyte, 1),
                ("_charging_timer",     c_ubyte, 1),
                ("_bit_6",              c_ubyte, 1),
                ("_pre_heating",        c_ubyte, 1),
                ("_bit_8",              c_ubyte, 1),
                ("_battery",            c_ubyte, 8),
    ]

    _byte_size_ = 2

    def _process_bytes(self):
        self.pm_sensor_status = bool(self._pm_sensor)
        self.error_flag = bool(self._error)
        self.bonding_flag = bool(self._bonding)
        self.charging = bool(self._charging)
        self.charging_timer = bool(self._charging_timer)
        self.pre_heating = bool(self._pre_heating)
        self.battery_level = self._battery

    def __str__(self):
        return (f"StatusPacket(timestamp={time.ctime(self.timestamp)}, "
                f"pm_sensor_status={self.pm_sensor_status}, "
                f"error_flag={self.error_flag}, "
                f"bonding_flag={self.bonding_flag}, "
                f"charging={self.charging}, "
                f"charging_timer={self.charging_timer}, "
                f"pre_heating={self.pre_heating}, "
                f"battery_level={self.battery_level}%)")


class SPS30Packet(AtmoTubePacket):
    _fields_ = [
        ('_pm1',   c_byte*3),
        ('_pm2_5', c_byte*3),
        ('_pm10',  c_byte*3),
        ('_pm4',   c_byte*3),
    ]

    _pack_ = 1
    _layout_ = "ms"
    _byte_size_ = 12

    def pm_from_bytes(self, byte_array):
        res = int.from_bytes(byte_array, byteorder='little', signed=True)
        return res/100.0 if res > 0 else None

    def _process_bytes(self):
        self.pm1 = self.pm_from_bytes(self._pm1)
        self.pm2_5 = self.pm_from_bytes(self._pm2_5)
        self.pm10 = self.pm_from_bytes(self._pm10)
        self.pm4 = self.pm_from_bytes(self._pm4)

    def __str__(self):
        return (f"SPS30Packet(timestamp={time.ctime(self.timestamp)}, "
                f"pm1={self.pm1}µg/m³, pm2_5={self.pm2_5}µg/m³, "
                f"pm10={self.pm10}µg/m³, pm4={self.pm4}µg/m³)")


class BME280Packet(AtmoTubePacket):
    _fields_ = [
        ('_rh',    c_byte),
        ('_T',     c_byte),
        ('_P',     c_int),
        ('_T_dec', c_short),
        ]

    _pack_ = 1
    _layout_ = "ms"
    _byte_size_ = 8

    def _process_bytes(self):
        self.humidity = self._rh if self._rh > 0 else None
        self.temperature = self._T_dec / 100.0
        self.pressure = self._P / 100.0 if self._P > 0 else None

    def __str__(self):
        return (f"BME280Packet(timestamp={time.ctime(self.timestamp)}, "
                f"humidity={self.humidity}%, "
                f"temperature={self.temperature}°C, "
                f"pressure={self.pressure}mbar)")


class SGPC3Packet(AtmoTubePacket):
    _fields_ = [
        ('_tvoc', c_short)
    ]

    _pack_ = 1
    _layout_ = "ms"
    _byte_size_ = 4

    def _process_bytes(self):
        self.tvoc = self._tvoc/1000.0 if self._tvoc > 0 else None

    def __str__(self):
        return (f"SGPC3Packet(timestamp={time.ctime(self.timestamp)}, "
                f"tvoc={self.tvoc}ppb)")
