from ctypes import LittleEndianStructure, c_ubyte, c_byte, c_short, c_int
import time

class AtmoTubePacket(LittleEndianStructure):
    def __new__(cls, data, ts=None):
        return cls.from_buffer_copy(data)

    def __init__(self, data, ts=None):
        if ts is None:
            ts = time.time()
        self.timestamp = ts
        self.__process_bytes__()

    def __process_bytes__(self):
        pass


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

    def __process_bytes__(self):
        self.pm_sensor_status = bool(self._pm_sensor)
        self.error_flag = bool(self._error)
        self.bonding_flag = bool(self._bonding)
        self.charging = bool(self._charging)
        self.charging_timer = bool(self._charging_timer)
        self.pre_heating = bool(self._pre_heating)
        self.battery_level = self._battery

class SPS30Packet(AtmoTubePacket):
    _fields_ = [
        ('_pm1',   c_byte*3),
        ('_pm2_5', c_byte*3),
        ('_pm10',  c_byte*3),
        ('_pm4',   c_byte*3), 
    ]
    _pack_ = 1

    def pm_from_bytes(self, byte_array):
        res = int.from_bytes(byte_array, byteorder='little', signed=True)
        return res/100.0 if res >0 else None

    def __process_bytes__(self):
        self.pm1 = self.pm_from_bytes(self._pm1)
        self.pm2_5 = self.pm_from_bytes(self._pm2_5)
        self.pm10 = self.pm_from_bytes(self._pm10)
        self.pm4 = self.pm_from_bytes(self._pm4)

class BME280Packet(AtmoTubePacket):
    _fields_ = [
        ('_rh',    c_byte),
        ('_T',     c_byte),
        ('_P',     c_int),
        ('_T_dec', c_short),
        ]
    _pack_ = 1

    def __process_bytes__(self):
        self.humidity = self._rh if self._rh > 0 else None
        self.temperature = self._T_dec / 100.0 # I'm not sure what the error condition is
        self.pressure = self._P / 100.0 if self._P > 0 else None

class SGPC3Packet(AtmoTubePacket):
    _fields_ = [
        ('_tvoc', c_short)
    ]
    _pack_ = 1

    def __process_bytes__(self):
        self.tvoc = self._tvoc/1000.0 if self._tvoc > 0 else None