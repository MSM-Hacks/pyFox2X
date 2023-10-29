import io
import json
import socket

from ... import sfs_types
from ...sfs_types import *


class SFSObject:
    __type: str = "undefined"
    __name: str
    __value: typing.Any

    def __init__(self, name: str = None, value=None):
        if value is None:
            value = {}
        if name is None:
            name = ""

        self.__type = "sfs_object"
        self.__name = name
        self.__value = value

    def __str__(self):
        from ..SFSArray import SFSArray

        result = f"(sfs_object) {self.getName()}:\n"
        for item_name, value in self.getValue().items():
            item_type = value[0]
            item_value = value[1]

            if item_type == "sfs_array":
                result += "\n".join(["    " + line for line in str(SFSArray(item_name, item_value)).split("\n")])
            elif item_type == "sfs_object":
                result += "\n".join(["    " + line for line in str(SFSObject(item_name, item_value)).split("\n")])[:-4]
            else:
                result += f"    {sfs_types.types[item_type](item_name, item_value)}\n"
        return result

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
        try:
            return name.decode('utf8'), other
        except:
            print("name err: ", str(name), "len: ", name_length)
            return "[name_err]", name+other

    @staticmethod
    def decompileName_conn(_conn: io.BytesIO) -> str:
        name_length = int.from_bytes(_conn.read(2), 'big')
        name = ""
        if 2:
            name = _conn.read(name_length).decode('utf8')
            return name
        # except:
        #     print("name err: ", str(name), "len: ", name_length)
        #     return "[name_err]"

    def compile(self) -> bytes:
        sfs_object = len(self.getValue().keys()).to_bytes(2, "big")
        for item_name, item_data in self.getValue().items():
            item_type = item_data[0]
            item_value = item_data[1]

            if item_type in sfs_types.types:
                obj = sfs_types.types[item_type](item_name, item_value)
                sfs_object += obj.compile()

        return self.compileName() + bytes([18]) + sfs_object

    @staticmethod
    def decompile(_bytes: bytes, decompile_name: bool = False, _step2: bool = False):
        if decompile_name:
            name, other = SFSObject.decompileName(_bytes)
            sfsObject = SFSObject(name)
        else:
            name, other = "", _bytes
            sfsObject = SFSObject()

        if not _step2:
            other = other[1:]

        length, other = int.from_bytes(other[0:2], 'big'), other[2:]
        for _ in range(length):
            key, other = SFSObject.decompileName(other)
            typex, other = int.from_bytes(other[:1], 'big'), other[1:]
            if typex > 18:
                continue
            if typex == 18:
                item, other = SFSObject.decompile(other, False, True)
            elif typex == 17:
                item, other = SFSArray.decompile(other, False, True)
            else:
                item, other = list(sfs_types.types.values())[typex].decompile(other, False)
            sfsObject.getValue()[key] = (list(sfs_types.types.keys())[typex], item.getValue())

        if _step2: return sfsObject, other
        return sfsObject

    @staticmethod
    def decompile_conn(_conn: io.BytesIO, decompile_name: bool = False, _step2: bool = False):
        if decompile_name:
            name = SFSObject.decompileName_conn(_conn)
            sfsObject = SFSObject(name)
        else:
            name = ""
            sfsObject = SFSObject()

        if not _step2:
            _conn.read(1)

        length = int.from_bytes(_conn.read(2), 'big')
        for _ in range(length):
            key = SFSObject.decompileName_conn(_conn)
            typex = int.from_bytes(_conn.read(1), 'big')
            if typex > 18:
                continue
            if typex == 18:
                item = SFSObject.decompile_conn(_conn, False, True)
            elif typex == 17:
                item = SFSArray.decompile_conn(_conn, False, True)
            else:
                item = list(sfs_types.types.values())[typex].decompile_conn(_conn, False)
            sfsObject.getValue()[key] = (list(sfs_types.types.keys())[typex], item.getValue())

        if _step2: return sfsObject
        return sfsObject

    def put(self, key: str, value):
        if value is None:
            self.putNull(key)
        elif type(value) in (int, bytes):
            if type(value) is int:
                value = bytes([value])

            if len(value) == 1:
                self.putByte(key, value)
            elif len(value) == 2:
                self.putShort(key, value)
            elif len(value) == 4:
                self.putInt(key, value)
            elif len(value) == 8:
                self.putLong(key, value)
            elif len(value) == 9:
                self.putDouble(key, value)
        elif type(value) is dict:
            self.putSFSObject(SFSObject.initFromPythonObject(value))
        elif type(value) is list:
            if len(value) > 0:
                if type(value[0]) is dict:
                    self.putSFSArray(key, value)
                elif type(value[0]) is float:
                    self.putDoubleArray(key, value)
                elif type(value[0]) is bool:
                    self.putBoolArray(key, value)
                elif type(value[0]) is str:
                    self.putUtfStringArray(key, value)
                elif type(value[0]) is int:
                    v = bytes([value[0]])
                    if len(v) == 1:
                        self.putByteArray(key, value)
                    else:
                        self.putInt(key, value)
        elif type(value) is str:
            self.putUtfString(key, value)
        elif type(value) is bool:
            self.putBool(key, value)
        elif type(value) is bytearray:
            self.putByteArray(key, value)

    def putNull(self, key: str):
        self.getValue()[key] = ("null", None)
        return self

    def putBool(self, key: str, value: bool):
        self.getValue()[key] = ("bool", value)
        return self

    def putByte(self, key: str, value: int):
        self.getValue()[key] = ("byte", value)
        return self

    def putShort(self, key: str, value: int):
        self.getValue()[key] = ("short", value)
        return self

    def putInt(self, key: str, value: int):
        self.getValue()[key] = ("int", value)
        return self

    def putLong(self, key: str, value: int):
        self.getValue()[key] = ("long", value)
        return self

    def putFloat(self, key: str, value: float):
        self.getValue()[key] = ("float", value)
        return self

    def putDouble(self, key: str, value: float):
        self.getValue()[key] = ("double", value)
        return self

    def putUtfString(self, key: str, value: str):
        self.getValue()[key] = ("utf_string", value)
        return self

    def putBoolArray(self, key: str, value: list):
        self.getValue()[key] = ("bool_array", value)
        return self

    def putByteArray(self, key: str, value: bytearray):
        self.getValue()[key] = ("byte_array", value)
        return self

    def putIntArray(self, key: str, value: list):
        self.getValue()[key] = ("int_array", value)
        return self

    def putShortArray(self, key: str, value: list):
        self.getValue()[key] = ("short_array", value)
        return self

    def putLongArray(self, key: str, value: list):
        self.getValue()[key] = ("long_array", value)
        return self

    def putFloatArray(self, key: str, value: list):
        self.getValue()[key] = ("float_array", value)
        return self

    def putDoubleArray(self, key: str, value: list):
        self.getValue()[key] = ("double_array", value)
        return self

    def putUtfStringArray(self, key: str, value: list):
        self.getValue()[key] = ("utf_string_array", value)
        return self

    def putSFSArray(self, key: str, value):
        self.getValue()[key] = ("sfs_array", value.getValue())
        return self

    def putSFSObject(self, key: str, value):
        self.getValue()[key] = ("sfs_object", value.getValue())
        return self

    def get(self, key: str):
        try:
            if self.getValue()[key][0] in ("sfs_object", "sfs_array"):
                return sfs_types.types[self.getValue()[key][0]](key, self.getValue()[key][1])
            else:
                return self.getValue()[key][1]
        except:
            return None

    @staticmethod
    def initFromPythonObject(python_object: dict):
        sfsObject = SFSObject()
        for key, value in python_object.items():
            sfsObject.put(key, value)

        return sfsObject

    @staticmethod
    def initWithJson(json_string: str):
        python_object = json.loads(json_string)
        sfsObject = SFSObject()
        for key, value in python_object.items():
            sfsObject.put(key, value)

        return sfsObject

    def getJsonDump(self, indent=None):
        val = {}
        for key, item in self.getValue().items():
            item = list(item)
            if item[0] == 'byte_array':
                item[1] = list(item[1])
            if item[0] in ('sfs_object', 'sfs_array'):
                item[1] = json.loads(sfs_types.types[item[0]](key, item[1]).getJsonDump())
            val[key] = item[1]
        return json.dumps(val, ensure_ascii=False, indent=indent)
