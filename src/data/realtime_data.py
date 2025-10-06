# Обмен данными с оборудованием стенда по ModbusTCP.
# Включает данные датчиков, состояния оборудования и управляющие команды.
# Все данные передаются в едином цикле обмена с периодом,
# установленным в переменной poll_interval.
# Обмен с ПЛК стенда происходит только в данном модуле.
import logging
import time
from ctypes import c_short

import numpy as np
from PyQt6.QtCore import (
    Qt,
    QThread,
    QTimer,
    QObject,
    pyqtSignal as Signal,
    pyqtSlot as Slot,
)
import asyncio
from pymodbus.client import ModbusTcpClient
from pymodbus.client import AsyncModbusTcpClient
from pymodbus.exceptions import ModbusException

REALTIME_DATA_WINDOW = 60  # временное окно для хранения данных (мин)


class ModbusPoller(QObject):
    """Background worker handling Modbus communication.

    Фоновый рабочий объект, управляющий обменом по Modbus.
    """

    data_received = Signal(list)
    connection_status = Signal(bool)

    def __init__(self, data_set):
        """Initialize worker with a reference to the data set.

        Инициализировать рабочий объект со ссылкой на набор данных.
        """
        QObject.__init__(self)
        self.data_set = data_set
        logging.debug('worker init')
        self.cfg = None
        self.client = None
        # self.init_modbus()
        self.tension = 0
        self.angle = 0
        self.result = None
        self.data_received.connect(self.data_set.update)
        """Настройка и запуск таймера опроса ПЛК."""
        self.timer = QTimer()
        self.timer.setTimerType(Qt.TimerType.PreciseTimer)
        self.timer.timeout.connect(self.on_timer)
        self.timer.start(self.data_set.poll_interval)

    async def poll_modbus(self):
        self.init_modbus()
        await self.client.connect()
        response = None
        try:
            response = await self.client.read_holding_registers(0, count=100, device_id=1)
        finally:
            if response is not None:
                self.data_received.emit(response.registers)
            self.client.close()

    def init_modbus(self):
        """Настройка Modbus клиента на основе конфигурации."""
        cfg = self.data_set.config
        host = cfg.get('modbus', 'host', '127.0.0.1')
        port = cfg.get('modbus', 'port', 502)
        timeout = cfg.get('modbus', 'timeout', 2.0)
        self.client = AsyncModbusTcpClient(host, port=port, timeout=timeout)
        self.register_address = 0  # Начальный адрес регистра для чтения
        self.register_qty = 10  # Количество регистров для чтения

    def safe_modbus_read(self, address, count=1, unit=1):
        """Безопасное чтение Modbus с обработкой ошибок соединения."""
        cfg = self.data_set.config
        host = cfg.get('modbus', 'host', '127.0.0.1')
        port = cfg.get('modbus', 'port', 502)
        timeout = cfg.get('modbus', 'timeout', 2.0)
        max_retries = cfg.get('modbus', 'retry_attempts', 3)
        client = None
        self.result = None

        for attempt in range(max_retries):
            try:
                client = ModbusTcpClient(host, port=port, timeout=timeout)

                if not client.connect():
                    raise ConnectionError("Не удалось установить соединение")

                self.result = client.read_holding_registers(
                    address, count=count, unit=unit
                )

                if self.result is None or self.result.isError():
                    raise Exception(f"Ошибка Modbus: {self.result}")

                return {
                    'status': 'успешно',
                    'data': self.result.registers,
                    'connected': True
                }

            except (ConnectionResetError, ConnectionError, OSError) as e:
                logging.warning(f"Попытка {attempt + 1}: Ошибка соединения - {e}")

                if attempt == max_retries - 1:
                    return {
                        'status': 'отсутствие соединения',
                        'data': None,
                        'connected': False,
                        'error': str(e)
                    }

                time.sleep(1)  # Пауза перед повторной попыткой

            except Exception as e:
                logging.error(f"Modbus read error: {e}")
                return {
                    'status': 'ошибка выполнения',
                    'data': None,
                    'connected': False,
                    'error': str(e)
                }

            finally:
                if client:
                    try:
                        client.close()
                    except Exception:
                        pass

        return {
            'status': 'отсутствие соединения',
            'data': None,
            'connected': False
        }

    @Slot()
    def on_timer(self):
        asyncio.run(self.poll_modbus())
        """Обработчик таймера опроса."""
        # self.get_data()

    @Slot()
    def get_data(self):
        """Получение данных от ПЛК и отправка их в основной поток."""
        try:
            self.result = self.client.readwrite_registers(
                read_address=self.register_address,
                read_count=self.register_qty,
                write_address=10,
                values=self.data_set.write_regs,
            )
            self.data_received.emit(self.result.registers)
        except ModbusException as e:
            logging.error(f"Modbus error: {e}")

class RealTimeData(QObject):
    """Хранение и обработка данных, получаемых по Modbus."""

    # arg#1: регистры Модбас (необработанные данные)
    # arg#2: новые данные от датчиков в формате [float, ...]
    data_updated = Signal(list)
    prev_time = 0

    def __init__(self, config, parent=None):
        """Инициализация параметров и запуск рабочего потока."""
        super(RealTimeData, self).__init__(parent)
        self.config = config

        # период опроса датчиков в миллисекундах
        self.poll_interval = self.config.get('ui', 'poll_interval_ms', 25)
        # период опроса в секундах
        self.poll_interval_s = float(self.poll_interval) / 1000.0
        # Длина массива данных с учётом периода опроса
        self.data_window_length = int(
            REALTIME_DATA_WINDOW * 60 * 1000 / self.poll_interval
        )

        # Слово состояния дискретных сигналов от ПЛК
        self.in_status = 0

        # данные от датчика угла поворота, в градусах
        self.angle_data = np.zeros(self.data_window_length, dtype=np.int32)

        # Данные от датчика угла поворота (преобразованные, в градусах)
        self.angle_data_c = np.zeros(self.data_window_length, dtype=np.float16)

        # данные от датчика крутящего момента, RAW АЦП
        self.tension_data = np.zeros(self.data_window_length, dtype=np.int16)

        # Данные от датчика крутящего момента (преобразованные к Нм)
        self.tension_data_c = np.zeros(self.data_window_length, dtype=np.float32)

        # Скорость нарастания момента (моментальные значения в Нм/с)
        self.velocity_data = np.zeros(self.data_window_length, dtype=np.float16)

        # временные метки для потока данных, в мс
        self.times = np.zeros(self.data_window_length, dtype=np.int64)
        self.ptr = 0  # Указатель текущей позиции данных

        # Текущие значения датчиков (данные ПЛК)
        self.tension_adc = 0        # Данные АЦП датчика момента
        self.tension_nc = 0         # Момент нескорректированный, Нм
        self.tension = 0            # Момент скорректированный, Нм
        self.angle = 0              # Угол поворота в градусах нескорректированный
        self.velocity = 0           # Скорость нарастания момента

        # Слово управления для отправки в ПЛК
        self.plc_control_word = 0
        self.write_regs = [0] * 6  # 6 шесть регистров для записи в ПЛК

        # Для обмена по Modbus создаем отдельный поток
        self.poller = ModbusPoller(self)
        self.poller_thread = QThread()
        # переносим worker в отдельный поток
        self.poller.moveToThread(self.poller_thread)
        # запускаем поток
        self.poller_thread.start()

        self.time_origin = time.time()  # Начальная временная метка для датасета
        self.prev_time = time.time()

    # Слот вызывается из ModbusPoller когда завершено получение новых данных от PLC
    @Slot(list)
    def update(self, registers):
        """Обновление данных по полученным регистрам."""
        self.times[self.ptr] = round((time.time() - self.time_origin) * 1000)
        self.tension_data_c[self.ptr] = self.get_real_tension(registers)
        self.angle_data_c[self.ptr] = self.get_real_angle(registers)
        self.velocity_data[self.ptr] = self.get_real_velocity()
        self.ptr += 1

        # Если массив заполнен, сдвигаем данные
        if self.ptr >= self.data_window_length:
            self.times[:-1] = self.times[1:]
            self.tension_data_c[:-1] = self.tension_data_c[1:]
            self.angle_data_c[:-1] = self.angle_data_c[1:]
            self.velocity_data[:-1] = self.velocity_data[1:]
            self.ptr = self.data_window_length - 1

        # Фиксируем текущие данные от датчика момента
        self.tension_adc = registers[1]
        self.tension_nc = self.get_real_tension_nc(registers)
        self.tension = self.get_real_tension(registers)

        # Фиксируем текущие данные от датчика угла
        self.angle = self.get_real_angle(registers)

        # Фиксируем текущую скорость нарастания момента
        self.velocity = self.velocity_data[self.ptr-1]

        # Считываем состояние регистров
        self.in_status = c_short(registers[0]).value
        self.data_updated.emit(registers)

    def get_real_tension_nc(self, registers):
        """Преобразование регистров в значение крутящего момента (нескорректированного)"""
        client = self.poller.client
        tension = client.convert_from_registers(registers[6:8], client.DATATYPE.FLOAT32)
        return tension

    def get_real_tension(self, registers):
        """Преобразование регистров в значение крутящего момента (корректированного в соответствии с калибровочной моделью)"""
        client = self.poller.client
        tension = client.convert_from_registers(registers[8:10], client.DATATYPE.FLOAT32)
        return tension

    def get_real_angle(self, registers):
        """Преобразование регистров в значение угла."""
        angle = float((registers[3] << 16) | registers[2]) / 768.0
        return angle

    def get_real_velocity(self):
        """Расчёт скорости нарастания момента."""
        velocity = 0.0
        if self.ptr > 0:
            velocity = (
                self.tension_data_c[self.ptr] - self.tension_data_c[self.ptr - 1]
            ) / self.poll_interval_s
        return velocity

    def get_dataset_by_name(self, dataset_name):
        """Возврат массива данных по имени."""
        match dataset_name:
            case 'tension_data_c':
                return self.tension_data_c
            case 'angle_data_c':
                return self.angle_data_c
            case 'velocity_data':
                return self.velocity_data

    @Slot(dict)
    def modbus_registers_to_PLC_update(self, regs):
        """Обновление регистров Modbus для записи в ПЛК."""
        for key, reg in regs.items():
            match key:
                case 'Modbus_CTRL':
                    self.write_regs[0] = reg
                case 'Modbus_TensionSV':
                    self.write_regs[1] = reg
                case 'Modbus_VelocitySV':
                    self.write_regs[2] = reg
                case 'Modbus_DQ_CTRL':
                    self.write_regs[3] = reg
                case 'Modbus_UZ_CTRL':
                    self.write_regs[4] = reg
                case 'Modbus_AUX':
                    self.write_regs[5] = reg

    @Slot()
    def update_connection_settings(self):
        """Применение настроек Modbus и периода опроса из конфигурации."""
        self.poll_interval = self.config.get('ui', 'poll_interval_ms', 25)
        self.poll_interval_s = float(self.poll_interval) / 1000.0
        if self.worker.timer:
            self.worker.timer.setInterval(self.poll_interval)
        self.worker.init_modbus()
