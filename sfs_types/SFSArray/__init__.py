import io
import json
import socket

from ... import sfs_types


class SFSArray:
    def __init__(self, name: str = None, value=None):
        if value is None:
            value = []
        if name is None:
            name = ""

        self.__type = "sfs_array"
        self.__name = name
        self.__value = value

        self.__iter = 0

    def __str__(self):
        result = f"(sfs_array) {self.getName()}:\n"
        for item_type, item_value in self.getValue():
            if item_type == "sfs_array":
                result += "\n".join(["    " + line for line in str(SFSArray("", item_value)).split("\n")])
            elif item_type == "sfs_object":
                result += "\n".join(["    " + line for line in str(sfs_types.SFSObject("", item_value)).split("\n")])[:-4]
            else:
                result += f"    ({item_type}): {item_value}\n"
        return result

    def __len__(self):
        return len(self.getValue())

    def __iter__(self):
        for _ in range(len(self)):
            yield self.get(_)
        return self

    def __getitem__(self, item):
        return self.get(item)

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

    def compile(self) -> bytes:
        array = int(len(self.getValue())).to_bytes(2, "big")
        for item in self.getValue():
            item_type = item[0]
            item_value = item[1]

            if item_type in sfs_types.types:
                array += sfs_types.types[item_type]("", item_value).compile()

        return bytes([17]) + self.compileName() + array

    @staticmethod
    def decompile(_bytes: bytes, decompile_name: bool = False, _step2: bool = False):
        if decompile_name:
            name, other = SFSArray.decompileName(_bytes)
            sfsObject = SFSArray(name)
        else:
            name, other = "", _bytes
            sfsObject = SFSArray()

        if not _step2:
            other = other[1:]

        length, other = int.from_bytes(other[0:2], 'big'), other[2:]
        for _ in range(length):
            typex, other = int.from_bytes(other[:1], 'big'), other[1:]
            if typex > 18:
                continue
            if typex == 18:
                item, other = sfs_types.SFSObject.decompile(other, False, True)
            elif typex == 17:
                item, other = SFSArray.decompile(other, False, True)
            else:
                item, other = list(sfs_types.types.values())[typex].decompile(other, False)
            sfsObject.getValue().append((list(sfs_types.types.keys())[typex], item.getValue()))

        if _step2: return sfsObject, other
        return sfsObject

    @staticmethod
    def decompile_conn(_conn: io.BytesIO, decompile_name: bool = False, _step2: bool = False):
        if decompile_name:
            name = SFSArray.decompileName_conn(_conn)
            sfsObject = SFSArray(name)
        else:
            name = ""
            sfsObject = SFSArray()

        if not _step2:
            _conn.read(1)

        length = int.from_bytes(_conn.read(2), 'big')
        for _ in range(length):
            typex = int.from_bytes(_conn.read(1), 'big')
            if typex > 18:
                continue
            if typex == 18:
                item = sfs_types.SFSObject.decompile_conn(_conn, False, True)
            elif typex == 17:
                item = SFSArray.decompile_conn(_conn, False, True)
            else:
                item = list(sfs_types.types.values())[typex].decompile_conn(_conn, False)
            sfsObject.getValue().append((list(sfs_types.types.keys())[typex], item.getValue()))

        if _step2: return sfsObject
        return sfsObject

    def add(self, value, index: int = None):
        from ..SFSObject import SFSObject
        if value is None:
            self.addNull(index)
        if type(value) in (int, bytes):
            if type(value) is int:
                value = bytes([value])

            if len(value) == 1:
                self.addByte(value, index)
            elif len(value) == 2:
                self.addShort(value, index)
            elif len(value) == 4:
                self.addInt(value, index)
            elif len(value) == 8:
                self.addLong(value, index)
            elif len(value) == 9:
                self.addDouble(value, index)
        elif type(value) is dict:
            self.addSFSObject(SFSObject.initFromPythonObject(value), index)
        elif type(value) is list:
            if len(value) > 0:
                if type(value[0]) is bool:
                    self.addBoolArray(value, index)
                elif type(value[0]) is float:
                    self.addDoubleArray(value, index)
                elif type(value[0]) is str:
                    self.addUtfStringArray(value, index)
                elif type(value[0]) is dict:
                    self.addSFSArray(value, index)
                elif type(value[0]) is int:
                    v = bytes([value[0]])
                    if len(v) == 1:
                        self.addByteArray(value, index)
                    else:
                        self.addInt(value, index)
        elif type(value) is str:
            self.addUtfString(value, index)
        elif type(value) is bool:
            self.addBool(value, index)
        elif type(value) is bytearray:
            self.addByteArray(value, index)

    def addNull(self, index: int = None):
        if index is None:
            self.getValue().append(("bool", None))
        else:
            self.getValue().insert(index, ("bool", None))

    def addBool(self, value: bool, index: int = None):
        if index is None:
            self.getValue().append(("bool", value))
        else:
            self.getValue().insert(index, ("bool", value))

    def addByte(self, value: int, index: int = None):
        if index is None:
            self.getValue().append(("byte", value))
        else:
            self.getValue().insert(index, ("byte", value))

    def addShort(self, value: int, index: int = None):
        if index is None:
            self.getValue().append(("short", value))
        else:
            self.getValue().insert(index, ("short", value))

    def addInt(self, value: int, index: int = None):
        if index is None:
            self.getValue().append(("int", value))
        else:
            self.getValue().insert(index, ("int", value))

    def addLong(self, value: int, index: int = None):
        if index is None:
            self.getValue().append(("long", value))
        else:
            self.getValue().insert(index, ("long", value))

    def addFloat(self, value: float, index: int = None):
        if index is None:
            self.getValue().append(("float", value))
        else:
            self.getValue().insert(index, ("float", value))

    def addDouble(self, value: float, index: int = None):
        if index is None:
            self.getValue().append(("double", value))
        else:
            self.getValue().insert(index, ("double", value))

    def addUtfString(self, value: str, index: int = None):
        if index is None:
            self.getValue().append(("utf_string", value))
        else:
            self.getValue().insert(index, ("utf_string", value))

    def addBoolArray(self, value: list, index: int = None):
        if index is None:
            self.getValue().append(("bool_array", value))
        else:
            self.getValue().insert(index, ("bool_array", value))

    def addByteArray(self, value: bytearray, index: int = None):
        if index is None:
            self.getValue().append(("byte_array", value))
        else:
            self.getValue().insert(index, ("byte_array", value))

    def addShortArray(self, value: list, index: int = None):
        if index is None:
            self.getValue().append(("short_array", value))
        else:
            self.getValue().insert(index, ("short_array", value))

    def addIntArray(self, value: list, index: int = None):
        if index is None:
            self.getValue().append(("int_array", value))
        else:
            self.getValue().insert(index, ("int_array", value))

    def addLongArray(self, value: list, index: int = None):
        if index is None:
            self.getValue().append(("long_array", value))
        else:
            self.getValue().insert(index, ("long_array", value))

    def addFloatArray(self, value: list, index: int = None):
        if index is None:
            self.getValue().append(("float_array", value))
        else:
            self.getValue().insert(index, ("float_array", value))

    def addDoubleArray(self, value: list, index: int = None):
        if index is None:
            self.getValue().append(("double_array", value))
        else:
            self.getValue().insert(index, ("double_array", value))

    def addUtfStringArray(self, value: list, index: int = None):
        if index is None:
            self.getValue().append(("utf_string_array", value))
        else:
            self.getValue().insert(index, ("utf_string_array", value))

    def addSFSArray(self, value, index: int = None):
        if index is None:
            self.getValue().append(("sfs_array", value))
        else:
            self.getValue().insert(index, ("sfs_array", value))

    def addSFSObject(self, value, index: int = None):
        if index is None:
            self.getValue().append(("sfs_object", value.getValue()))
        else:
            self.getValue().insert(index, ("sfs_object", value.getValue()))

    def get(self, index: int):
        if self.getValue()[index][0] in ("sfs_object", "sfs_array"):
            return sfs_types.types[self.getValue()[index][0]]("", self.getValue()[index][1])
        return self.getValue()[index][1]

    @staticmethod
    def initFromPythonObject(python_object: list):
        sfsArray = SFSArray()
        for value in python_object:
            sfsArray.add(value)

        return sfsArray

    @staticmethod
    def initWithJson(json_string: str):
        python_object = json.loads(json_string)
        sfsArray = SFSArray()
        for value in python_object:
            sfsArray.add(value)

        return sfsArray

    def getJsonDump(self):
        val = []
        for item in self.getValue():
            item = list(item)
            if item[0] == "byte_array":
                val.append(list(item[1]))
            elif item[0] in ('sfs_object', 'sfs_array'):
                item[1] = json.loads(sfs_types.types[item[0]]("", item[1]).getJsonDump())
            else:
                val.append(item[1])
        return json.dumps(val, ensure_ascii=False)
