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

### 3. Подключение к серверу

```
from pyfox2x.sfs_types.SFSObject import SFSObject
from pyfox2x.sfs_types.SFSArray import SFSArray
from pyfox2x.sfs_client import SFSClient

auth_params = SFSObject()
auth_params.putUtfString('user_id', 'Kmdinndsdfcn')
auth_params.putUtfString('client_os', '12')
auth_params.putUtfString('client_platform', 'android')
auth_params.putUtfString('client_version', '3.1.1')

client = SFSClient()
client.connect(host='127.0.0.1', port=9933)
client.send_login_request('ZoneName', 'username', 'password', auth_params)
```

В этом примере создается объект auth_params класса SFSObject, в котором добавляются различные параметры авторизации. Затем создается объект client класса SFSClient и устанавливается соединение с сервером, указывая хост и порт. Наконец, отправляется запрос на авторизацию, указывая название зоны, имя пользователя, пароль и параметры авторизации.

### 4. Общение с сервером

В библиотеке pyFox2X вы можете отправлять запросы на сервер и ожидать ответы от него. Для этого доступны следующие методы:

#### Отправка запроса и ожидание ответа

```python
player_object = client.request('get_player_data', SFSObject().putLong("last_updated", 0)).get("player_object")
```

В приведенном примере отправляется запрос с именем 'get_player_data' и параметром 'last_updated'. Ожидается ответ от сервера, и значение поле "player_object" из ответа записывается в переменную 'player_object'.

#### Отправка запроса без ожидания ответа

```python
client.send_extension_request('collect_coins_from_monster', SFSObject().putLong("user_monster_id", 199))
```

В этом примере отправляется запрос с именем 'collect_coins_from_monster' и параметром 'user_monster_id'. Запрос отправляется на сервер, но ответ не ожидается.

#### Ожидание ответа без отправки запроса

```python
response = client.wait_extension_response('giveaway')
```

В данном примере ожидается ответ от сервера с именем 'giveaway'. Метод блокируется до получения ответа, и значение ответа записывается в переменную 'response'.

#### Ожидание одного из нескольких пакетов

```python
cmd, response = client.wait_requests(['login_success', 'login_failed', 'player_banned'])
```


