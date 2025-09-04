from abc import ABC, abstractmethod
from typing import Any


class DataSource(ABC):
    """Абстрактный базовый класс для всех источников данных"""

    @abstractmethod
    def connect(self) -> bool:
        """Установить соединение с источником данных"""
        pass

    @abstractmethod
    def disconnect(self) -> None:
        """Закрыть соединение"""
        pass

    @abstractmethod
    def read_data(self) -> dict[str, Any]:
        """Прочитать данные"""
        pass

    @abstractmethod
    def write_data(self, data: dict[str, Any]) -> None:
        pass

    @abstractmethod
    def is_connected(self) -> bool:
        """Проверить состояние соединения"""
        pass


# Реальная реализация для Modbus
class ModbusDataSource(DataSource):
    def __init__(self, host: str, port: int):
        self.host = host
        self.port = port
        self.client = None
        self._connected = False

    def connect(self) -> bool:
        print(f"Подключение к Modbus {self.host}:{self.port}")
        # Здесь код подключения к Modbus
        self._connected = True
        return True

    def disconnect(self) -> None:
        print("Отключение от Modbus")
        self._connected = False

    def read_data(self) -> dict[str, Any]:
        if not self._connected:
            raise ConnectionError("Не подключен к Modbus")

        # Реальное чтение данных из регистров
        return {
            "torque": 45.2,
            "speed": 3.1,
            "angle": 180.0,
            "temperature": 22.5
        }

    def write_data(self, data: dict[str, Any]) -> None:
        pass

    def is_connected(self) -> bool:
        return self._connected


# Mock реализация для тестирования
class MockDataSource(DataSource):
    def __init__(self):
        self._connected = False
        self.call_count = 0

    def connect(self) -> bool:
        print("Подключение к Mock источнику")
        self._connected = True
        return True

    def disconnect(self) -> None:
        print("Отключение от Mock источника")
        self._connected = False

    def read_data(self) -> dict[str, Any]:
        self.call_count += 1
        import random
        return {
            "torque": random.uniform(0, 100),
            "speed": random.uniform(0, 10),
            "angle": random.uniform(0, 360),
            "temperature": random.uniform(20, 30)
        }

    def write_data(self, data: dict[str, Any]) -> None:
        pass

    def is_connected(self) -> bool:
        return self._connected


# Файловая реализация
class FileDataSource(DataSource):
    def __init__(self, filename: str):
        self.filename = filename
        self._connected = False

    def connect(self) -> bool:
        try:
            with open(self.filename, 'r') as f:
                self._connected = True
            return True
        except FileNotFoundError:
            return False

    def disconnect(self) -> None:
        self._connected = False

    def read_data(self) -> dict[str, Any]:
        if not self._connected:
            raise ConnectionError("Файл не открыт")

        with open(self.filename, 'r') as f:
            import json
            return json.load(f)

    def write_data(self, data: dict[str, Any]) -> None:
        pass

    def is_connected(self) -> bool:
        return self._connected


# Использование
def process_data(data_source: DataSource):
    """Функция работает с любым источником данных"""
    if data_source.connect():
        try:
            data = data_source.read_data()
            print(f"Получены данные: {data}")
        finally:
            data_source.disconnect()
    else:
        print("Не удалось подключиться к источнику данных")


# # Примеры использования
# modbus_source = ModbusDataSource("192.168.1.100", 502)
# mock_source = MockDataSource()
# file_source = FileDataSource("data.json")
#
# process_data(modbus_source)  # Работает с Modbus
# process_data(mock_source)  # Работает с Mock
# process_data(file_source)  # Работает с файлом
