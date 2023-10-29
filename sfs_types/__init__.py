import io
import socket
import struct
import typing

from pyfox2x.sfs_types.SFSArray import SFSArray
from pyfox2x.sfs_types.SFSObject import SFSObject


class BaseType:
    __type: str = "undefined"
    __name: str
    __value: typing.Any

    def __init__(self, object_type: str, name: str, value):
        self.__type = object_type
        self.__name = name
        self.__value = value

    def __str__(self) -> str:
        return f"({self.__type}) {self.__name}: {self.__value}"

    def getName(self):
        return self.__name

    def getValue(self):
        return self.__value

    def compileName(self) -> bytes:
        if self.__name != "":
            return len(self.__name).to_bytes(2, 'big') + self.__name.encode('utf-8')
        else:
            return b''

    @staticmethod
    def decompileName(_bytes: bytes) -> (str, bytes):
        name_length = int.from_bytes(_bytes[:2], 'big')
        name, other = _bytes[2: name_length + 2], _bytes[name_length + 2:]
        return name.decode('utf8'), other

    @staticmethod
    def decompileName_conn(_conn: io.BytesIO) -> str:
        name_length = int.from_bytes(_conn.read(2), 'big')
        name = _conn.read(name_length)
        return name.decode('utf8')


class Null(BaseType):
    def __init__(self, name: str, value: None):
        super().__init__("null", name, None)

    def compile(self) -> bytes:
        return super().compileName() + bytes([0])

    @staticmethod
    def decompile(_bytes: bytes, decompile_name: bool = True):
        return Byte("TODO: Fix this shit", 0), _bytes[1:]

    @staticmethod
    def decompile_conn(_conn: io.BytesIO, decompile_name: bool = True):
        _conn.read(1)
        return Byte("TODO: Fix this shit", 0)


class Bool(BaseType):
    def __init__(self, name: str, value: bool):
        super().__init__("bool", name, value)

    def compile(self) -> bytes:
        return super().compileName() + bytes([1]) + int(super().getValue()).to_bytes(1, "big")

    @staticmethod
    def decompile(_bytes: bytes, decompile_name: bool = True):
        if decompile_name:
            name, other = BaseType.decompileName(_bytes)
        else:
            name, other = "", _bytes
        return Bool(name, bool.from_bytes(other[:1], 'big')), other[1:]

    @staticmethod
    def decompile_conn(_conn: io.BytesIO, decompile_name: bool = True):
        if decompile_name:
            name = BaseType.decompileName_conn(_conn)
        else:
            name = ""
        return Bool(name, bool.from_bytes(_conn.read(1), 'big'))


class Byte(BaseType):
    def __init__(self, name: str, value):
        if type(value) is int:
            value = value.to_bytes(1, "big", signed=True)
        super().__init__("byte", name, value)

    def compile(self) -> bytes:
        return super().compileName() + bytes([2]) + super().getValue()

    @staticmethod
    def decompile(_bytes: bytes, decompile_name: bool = True):
        if decompile_name:
            name, other = BaseType.decompileName(_bytes)
        else:
            name, other = "", _bytes
        return Byte(name, int.from_bytes(other[:1], 'big', signed=True)), other[1:]

    @staticmethod
    def decompile_conn(_conn: io.BytesIO, decompile_name: bool = True):
        if decompile_name:
            name = BaseType.decompileName_conn(_conn)
        else:
            name = ""
        return Byte(name, int.from_bytes(_conn.read(1), 'big', signed=True))


class Short(BaseType):
    def __init__(self, name: str, value: int):
        super().__init__("short", name, value)

    def compile(self) -> bytes:
        return super().compileName() + bytes([3]) + super().getValue().to_bytes(2, "big", signed=True)

    @staticmethod
    def decompile(_bytes: bytes, decompile_name: bool = True):
        if decompile_name:
            name, other = BaseType.decompileName(_bytes)
        else:
            name, other = "", _bytes
        return Short(name, int.from_bytes(other[:2], 'big', signed=True)), other[2:]

    @staticmethod
    def decompile_conn(_conn: io.BytesIO, decompile_name: bool = True):
        if decompile_name:
            name = BaseType.decompileName_conn(_conn)
        else:
            name = ""
        return Short(name, int.from_bytes(_conn.read(2), 'big', signed=True))


class Int(BaseType):
    def __init__(self, name: str, value: int):
        super().__init__("int", name, value)

    def compile(self) -> bytes:
        return super().compileName() + bytes([4]) + super().getValue().to_bytes(4, "big", signed=True)

    @staticmethod
    def decompile(_bytes: bytes, decompile_name: bool = True):
        if decompile_name:
            name, other = BaseType.decompileName(_bytes)
        else:
            name, other = "", _bytes
        return Int(name, int.from_bytes(other[:4], 'big', signed=True)), other[4:]

    @staticmethod
    def decompile_conn(_conn: io.BytesIO, decompile_name: bool = True):
        if decompile_name:
            name = BaseType.decompileName_conn(_conn)
        else:
            name = ""
        return Int(name, int.from_bytes(_conn.read(4), 'big', signed=True))


class Long(BaseType):
    def __init__(self, name: str, value: int):
        super().__init__("long", name, value)

    def compile(self) -> bytes:
        return super().compileName() + bytes([5]) + super().getValue().to_bytes(8, "big", signed=True)

    @staticmethod
    def decompile(_bytes: bytes, decompile_name: bool = True):
        if decompile_name:
            name, other = BaseType.decompileName(_bytes)
        else:
            name, other = "", _bytes
        return Long(name, int.from_bytes(other[:8], 'big', signed=True)), other[8:]

    @staticmethod
    def decompile_conn(_conn: io.BytesIO, decompile_name: bool = True):
        if decompile_name:
            name = BaseType.decompileName_conn(_conn)
        else:
            name = ""
        return Long(name, int.from_bytes(_conn.read(8), 'big', signed=True))


class Float(BaseType):
    def __init__(self, name: str, value: float):
        super().__init__("float", name, value)

    def compile(self) -> bytes:
        return super().compileName() + bytes([6]) + int.from_bytes(struct.pack("f", super().getValue()),
                                                                   "little", signed=True).to_bytes(4, "big", signed=True)

    @staticmethod
    def decompile(_bytes: bytes, decompile_name: bool = True):
        if decompile_name:
            name, other = BaseType.decompileName(_bytes)
        else:
            name, other = "", _bytes
        return Float(name, round(struct.unpack('f', other[:4][::-1])[0], 6)), other[4:]

    @staticmethod
    def decompile_conn(_conn: io.BytesIO, decompile_name: bool = True):
        if decompile_name:
            name = BaseType.decompileName_conn(_conn)
        else:
            name = ""
        return Float(name, round(struct.unpack('f', _conn.read(4)[::-1])[0], 6))


class Double(BaseType):
    def __init__(self, name: str, value: float):
        super().__init__("double", name, value)

    def compile(self) -> bytes:
        return super().compileName() + bytes([7]) + int.from_bytes(struct.pack("d", super().getValue()),
                                                                   "big", signed=True).to_bytes(8, "big", signed=True)

    @staticmethod
    def decompile(_bytes: bytes, decompile_name: bool = True):
        if decompile_name:
            name, other = BaseType.decompileName(_bytes)
        else:
            name, other = "", _bytes
        return Double(name, struct.unpack('d', other[:8])[0]), other[8:]

    @staticmethod
    def decompile_conn(_conn: io.BytesIO, decompile_name: bool = True):
        if decompile_name:
            name = BaseType.decompileName_conn(_conn)
        else:
            name = ""
        return Double(name, struct.unpack('d', _conn.read(8))[0])


class UtfString(BaseType):
    def __init__(self, name: str, value: str):
        super().__init__("utf_string", name, value)

    def compile(self) -> bytes:
        return super().compileName() + bytes([8]) + len(super().getValue()).to_bytes(2, "big") + \
            super().getValue().encode("utf-8")

    @staticmethod
    def decompile(_bytes: bytes, decompile_name: bool = True):
        if decompile_name:
            name, other = BaseType.decompileName(_bytes)
        else:
            name, other = "", _bytes

        length = int.from_bytes(other[:2], 'big')
        return UtfString(name, other[2:length+2].decode('utf8')), other[length+2:]

    @staticmethod
    def decompile_conn(_conn: io.BytesIO, decompile_name: bool = True):
        if decompile_name:
            name = BaseType.decompileName_conn(_conn)
        else:
            name = ""
        length = int.from_bytes(_conn.read(2), 'big')
        return UtfString(name, _conn.read(length).decode('utf8'))


class BoolArray(BaseType):
    def __init__(self, name: str, value: list):
        super().__init__("bool_array", name, value)

    def compile(self) -> bytes:
        result = super().compileName() + bytes([9]) + int(len(super().getValue()) - 1).to_bytes(2, "big")
        for byte in super().getValue():
            result += bytes([byte])
        return result

    @staticmethod
    def decompile(_bytes: bytes, decompile_name: bool = True):
        if decompile_name:
            name, other = BaseType.decompileName(_bytes)
        else:
            name, other = "", _bytes

        length, other = int.from_bytes(other[:2], 'big'), other[2:]
        array = []
        for _ in range(length):
            array.append(bool.from_bytes(other[:1], "big"))
            other = other[1:]
        return BoolArray(name, array), other

    @staticmethod
    def decompile_conn(_conn: io.BytesIO, decompile_name: bool = True):
        if decompile_name:
            name = BaseType.decompileName_conn(_conn)
        else:
            name = ""

        length = int.from_bytes(_conn.read(2), 'big')
        array = []
        for _ in range(length):
            array.append(bool.from_bytes(_conn.read(1), "big"))
        return BoolArray(name, array)


class ByteArray(BaseType):
    def __init__(self, name: str, value):
        super().__init__("byte_array", name, value)

    def compile(self) -> bytes:
        result = super().compileName() + bytes([10]) + int(len(super().getValue()) - 1).to_bytes(4, "big")
        for byte in super().getValue():
            result += bytes([byte])
        return result

    @staticmethod
    def decompile(_bytes: bytes, decompile_name: bool = True):
        if decompile_name:
            name, other = BaseType.decompileName(_bytes)
        else:
            name, other = "", _bytes

        length, other = int.from_bytes(other[:4], 'big'), other[4:]
        array = bytearray()
        for _ in range(length):
            array += other[:1]
            other = other[1:]
        return ByteArray(name, array), other

    @staticmethod
    def decompile_conn(_conn: io.BytesIO, decompile_name: bool = True):
        if decompile_name:
            name = BaseType.decompileName_conn(_conn)
        else:
            name = ""

        length = int.from_bytes(_conn.read(4), 'big')
        array = bytearray()
        for _ in range(length):
            array += _conn.read(1)
        return ByteArray(name, array)


class ShortArray(BaseType):
    def __init__(self, name: str, value: list):
        super().__init__("short_array", name, value)

    def compile(self) -> bytes:
        result = super().compileName() + bytes([11]) + int(len(super().getValue()) - 1).to_bytes(2, "big")
        for byte in super().getValue():
            result += byte.to_bytes(2, "big", signed=True)
        return result

    @staticmethod
    def decompile(_bytes: bytes, decompile_name: bool = True):
        if decompile_name:
            name, other = BaseType.decompileName(_bytes)
        else:
            name, other = "", _bytes

        length, other = int.from_bytes(other[:2], 'big'), other[2:]
        array = []
        for _ in range(length):
            array.append(int.from_bytes(other[:2], 'big', signed=True))
            other = other[2:]
        return ShortArray(name, array), other

    @staticmethod
    def decompile_conn(_conn: io.BytesIO, decompile_name: bool = True):
        if decompile_name:
            name = BaseType.decompileName_conn(_conn)
        else:
            name = ""

        length = int.from_bytes(_conn.read(2), 'big')
        array = []
        for _ in range(length):
            array.append(int.from_bytes(_conn.read(2), 'big', signed=True))
        return ShortArray(name, array)


class IntArray(BaseType):
    def __init__(self, name: str, value: list):
        super().__init__("int_array", name, value)

    def compile(self) -> bytes:
        result = super().compileName() + bytes([12]) + int(len(super().getValue()) - 1).to_bytes(2, "big", signed=True)
        for byte in super().getValue():
            result += byte.to_bytes(4, "big", signed=True)
        return result

    @staticmethod
    def decompile(_bytes: bytes, decompile_name: bool = True):
        if decompile_name:
            name, other = BaseType.decompileName(_bytes)
        else:
            name, other = "", _bytes

        length, other = int.from_bytes(other[:2], 'big'), other[2:]
        array = []
        for _ in range(length):
            array.append(int.from_bytes(other[:4], 'big', signed=True))
            other = other[4:]
        return IntArray(name, array), other

    @staticmethod
    def decompile_conn(_conn: io.BytesIO, decompile_name: bool = True):
        if decompile_name:
            name = BaseType.decompileName_conn(_conn)
        else:
            name = ""

        length = int.from_bytes(_conn.read(2), 'big')
        array = []
        for _ in range(length):
            array.append(int.from_bytes(_conn.read(4), 'big', signed=True))
        return IntArray(name, array)


class LongArray(BaseType):
    def __init__(self, name: str, value: list):
        super().__init__("long_array", name, value)

    def compile(self) -> bytes:
        result = super().compileName() + bytes([13]) + int(len(super().getValue()) - 1).to_bytes(2, "big")
        for byte in super().getValue():
            result += byte.to_bytes(8, "big", signed=True)
        return result

    @staticmethod
    def decompile(_bytes: bytes, decompile_name: bool = True):
        if decompile_name:
            name, other = BaseType.decompileName(_bytes)
        else:
            name, other = "", _bytes

        length, other = int.from_bytes(other[:2], 'big'), other[2:]
        array = []
        for _ in range(length):
            array.append(int.from_bytes(other[:8], 'big', signed=True))
            other = other[8:]
        return LongArray(name, array), other

    @staticmethod
    def decompile_conn(_conn: io.BytesIO, decompile_name: bool = True):
        if decompile_name:
            name = BaseType.decompileName_conn(_conn)
        else:
            name = ""

        length = int.from_bytes(_conn.read(2), 'big')
        array = []
        for _ in range(length):
            array.append(int.from_bytes(_conn.read(4), 'big', signed=True))
        return LongArray(name, array)


class FloatArray(BaseType):
    def __init__(self, name: str, value: list):
        super().__init__("float_array", name, value)

    def compile(self) -> bytes:
        result = super().compileName() + bytes([14]) + int(len(super().getValue()) - 1).to_bytes(2, "big")
        for byte in super().getValue():
            result += int.from_bytes(struct.pack("f", byte), "little", signed=True).to_bytes(
                4, "big", signed=True)
        return result

    @staticmethod
    def decompile(_bytes: bytes, decompile_name: bool = True):
        if decompile_name:
            name, other = BaseType.decompileName(_bytes)
        else:
            name, other = "", _bytes

        length, other = int.from_bytes(other[:2], 'big'), other[2:]
        array = []
        for _ in range(length ):
            array.append(round(struct.unpack('f', other[:4][::-1])[0], 6))
            other = other[4:]
        return FloatArray(name, array), other

    @staticmethod
    def decompile_conn(_conn: io.BytesIO, decompile_name: bool = True):
        if decompile_name:
            name = BaseType.decompileName_conn(_conn)
        else:
            name = ""

        length = int.from_bytes(_conn.read(2), 'big')
        array = []
        for _ in range(length ):
            array.append(round(struct.unpack('f', _conn.read(4)[::-1])[0], 6))
        return FloatArray(name, array)


class DoubleArray(BaseType):
    def __init__(self, name: str, value: list):
        super().__init__("double_array", name, value)

    def compile(self) -> bytes:
        result = super().compileName() + bytes([15]) + int(len(super().getValue()) - 1).to_bytes(2, "big")
        for byte in super().getValue():
            result += int.from_bytes(struct.pack("d", byte), "little", signed=True).to_bytes(
                8, "big", signed=True)
        return result

    @staticmethod
    def decompile(_bytes: bytes, decompile_name: bool = True):
        if decompile_name:
            name, other = BaseType.decompileName(_bytes)
        else:
            name, other = "", _bytes

        length, other = int.from_bytes(other[:2], 'big'), other[2:]
        array = []
        for _ in range(length):
            array.append(round(struct.unpack('d', other[:8][::-1])[0], 12))
            other = other[8:]
        return DoubleArray(name, array), other

    @staticmethod
    def decompile_conn(_conn: io.BytesIO, decompile_name: bool = True):
        if decompile_name:
            name = BaseType.decompileName_conn(_conn)
        else:
            name = ""

        length = int.from_bytes(_conn.read(2), 'big')
        array = []
        for _ in range(length):
            array.append(round(struct.unpack('d', _conn.read(8)[::-1])[0], 12))
        return DoubleArray(name, array)


class UtfStringArray(BaseType):
    def __init__(self, name: str, value: list):
        super().__init__("utf_string_array", name, value)

    def compile(self) -> bytes:
        result = super().compileName() + bytes([16]) + int(len(super().getValue()) - 1).to_bytes(2, "big")
        for byte in super().getValue():
            result += len(byte).to_bytes(2, "big") + byte.encode("utf-8")
        return result

    @staticmethod
    def decompile(_bytes: bytes, decompile_name: bool = True):
        if decompile_name:
            name, other = BaseType.decompileName(_bytes)
        else:
            name, other = "", _bytes

        length, other = int.from_bytes(other[:2], 'big'), other[2:]
        array = []
        for _ in range(length):
            string_length, other = int.from_bytes(other[:2], 'big'), other[2:]
            array.append(other[:string_length].decode("utf-8"))
            other = other[string_length:]
        return UtfStringArray(name, array), other

    @staticmethod
    def decompile_conn(_conn: io.BytesIO, decompile_name: bool = True):
        if decompile_name:
            name = BaseType.decompileName_conn(_conn)
        else:
            name = ""

        length = int.from_bytes(_conn.read(2), 'big')
        array = []
        for _ in range(length):
            string_length = int.from_bytes(_conn.read(2), 'big')
            array.append(_conn.read(string_length).decode("utf-8"))
        return UtfStringArray(name, array)


types = {
    "null": Null,
    "bool": Bool,
    "byte": Byte,
    "short": Short,
    "int": Int,
    "long": Long,
    "float": Float,
    "double": Double,
    "utf_string": UtfString,
    "bool_array": BoolArray,
    "byte_array": ByteArray,
    "short_array": ShortArray,
    "int_array": IntArray,
    "long_array": LongArray,
    "float_array":  FloatArray,
    "double_array": DoubleArray,
    "utf_string_array": UtfStringArray,
    "sfs_array": SFSArray,
    "sfs_object": SFSObject
}