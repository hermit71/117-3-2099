from abc import ABC, abstractmethod
from typing import Any
import logging


logger = logging.getLogger(__name__)


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
    """Data source for real Modbus communication."""

    def __init__(self, host: str, port: int):
        self.host = host
        self.port = port
        self.client = None
        self._connected = False

    def connect(self) -> bool:
        logger.info("Подключение к Modbus %s:%s", self.host, self.port)
        # Здесь код подключения к Modbus
        self._connected = True
        return True

    def disconnect(self) -> None:
        logger.info("Отключение от Modbus")
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
        """Write data to Modbus registers.

        Raises:
            NotImplementedError: Writing to Modbus is not implemented.
        """
        raise NotImplementedError("Writing data to Modbus is not implemented")

    def is_connected(self) -> bool:
        return self._connected


# Mock реализация для тестирования
class MockDataSource(DataSource):
    """Mock data source used for testing without hardware."""

    def __init__(self):
        self._connected = False
        self.call_count = 0

    def connect(self) -> bool:
        logger.info("Подключение к Mock источнику")
        self._connected = True
        return True

    def disconnect(self) -> None:
        logger.info("Отключение от Mock источника")
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
        """Store data to mimic writing in tests."""
        self.last_written_data = data
        logger.info("Mock write data: %s", data)

    def is_connected(self) -> bool:
        return self._connected


# Файловая реализация
class FileDataSource(DataSource):
    """Data source backed by a JSON file."""

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
        """Write data to the file in JSON format."""
        if not self._connected:
            raise ConnectionError("Файл не открыт")
        with open(self.filename, 'w') as f:
            import json
            json.dump(data, f)

    def is_connected(self) -> bool:
        return self._connected


# Использование
def process_data(data_source: DataSource):
    """Функция работает с любым источником данных"""
    if data_source.connect():
        try:
            data = data_source.read_data()
            logger.info("Получены данные: %s", data)
        finally:
            data_source.disconnect()
    else:
        logger.error("Не удалось подключиться к источнику данных")


# # Примеры использования
# modbus_source = ModbusDataSource("192.168.1.100", 502)
# mock_source = MockDataSource()
# file_source = FileDataSource("data.json")
#
# process_data(modbus_source)  # Работает с Modbus
# process_data(mock_source)  # Работает с Mock
# process_data(file_source)  # Работает с файлом
