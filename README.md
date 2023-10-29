# pyFox2X - реализация протокола SFS2x на Python

pyFox2X - это библиотека на языке Python, которая предоставляет реализацию протокола SFS2X (SmartFoxServer 2X) для работы с объектами и массивами данных. Библиотека позволяет создавать и манипулировать объектами и массивами, получать данные из них, также в ней реализована компиляция и декомпиляция пакетов и функции общения с серверами.

## Примеры использования

### 1. Работа с объектами

```
from pyfox2x.sfs_types.SFSObject import SFSObject

obj = SFSObject()
obj.putInt('name', 12)
obj.putBool('name_2', False)

a: int = obj.getInt('name')
```

В приведенном примере создается объект obj класса SFSObject. Затем используются методы putInt и putBool для добавления данных в объект.

### 2. Работа с массивами

```
from pyfox2x.sfs_types.SFSArray import SFSArray

arr = SFSArray()
arr.addInt(12)
arr.addLong(324233242)

b: int = arr.getLong(1)
```


В данном примере создается массив arr класса SFSArray. С помощью методов addInt и addLong данные добавляются в массив.

## Как использовать?

Чтобы начать использовать pyFox2X, необходимо установить библиотеку и импортировать классы SFSObject и SFSArray из модулей SFSObject и SFSArray соответственно.

```
from pyfox2x.sfs_types.SFSObject import SFSObject
from pyfox2x.sfs_types.SFSArray import SFSArray
```

После этого вы можете создавать объекты и массивы данных, добавлять данные в них и получать данные из них, следуя приведенным выше примерам.

## Лицензия

Этот проект лицензируется под MIT License
