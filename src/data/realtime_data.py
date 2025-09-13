# Обмен данными с оборудованием стенда по ModbusTCP
# Включает в себя данные датчиков, данные состояния оборудования и управляющие команды
# Все данные передаются в едином цикле обмена с периодом установленным в переменной poll_inteval
# Обмен данными с ПЛК стенда в программе управления стендом происходит ТОЛЬКО в данном модуле!
import logging
import time
from ctypes import c_short

import numpy as np
from PyQt6.QtCore import Qt, QThread, QTimer, QObject, pyqtSignal as Signal, pyqtSlot as Slot
from pymodbus.client import ModbusTcpClient
from pymodbus.exceptions import ModbusException
REALTIME_DATA_WINDOW = 60  # час - временное окно для хранения данных от датчиков в реальном времени в минутах


class Worker(QObject):
    """Background worker handling Modbus communication."""

    data_received = Signal(list)
    connection_status = Signal(bool)

    def __init__(self, data_set):
        """Initialize worker with a reference to the data set."""
        QObject.__init__(self)
        self.data_set = data_set
        logging.debug('worker init')
        self.init_modbus()
        self.data_received.connect(self.data_set.update)
        self.timer = None
        self.tension = 0
        self.angle = 0
        self.result = None

    def start(self):
        """Настройка и запуск таймера опроса ПЛК."""
        self.timer = QTimer()
        self.timer.setTimerType(Qt.TimerType.PreciseTimer)
        self.timer.timeout.connect(self.on_timer)
        self.timer.start(self.data_set.poll_interval)
        self.tension = 0
        self.angle = 0
        self.result = None

    def init_modbus(self):
        """Настройка Modbus клиента."""
        self.client = ModbusTcpClient('192.168.6.31')  # IP-адрес PLC ('127.0.0.1')
        self.register_address = 0  # Начальный адрес регистра для чтения
        self.register_qty = 7  # Количество регистров для чтения

    def safe_modbus_read(self, host, port, address, count=1, unit=1, max_retries=3):
        """Безопасное чтение Modbus с обработкой ошибок соединения."""
        client = None
        self.result = None

        for attempt in range(max_retries):
            try:
                client = ModbusTcpClient(host, port=port)

                if not client.connect():
                    raise ConnectionError("Не удалось установить соединение")

                self.result = client.read_holding_registers(address, count=count, unit=unit)

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
        """Обработчик таймера опроса."""
        self.get_data()
        # self.safe_modbus_read("", "", "")

    @Slot()
    def get_data(self):
        """Получение данных от ПЛК и отправка их в основной поток."""
        try:
            # self.result = self.client.read_holding_registers(self.register_address, count=self.register_qty)
            self.result = self.client.readwrite_registers(
                read_address=self.register_address,
                read_count=self.register_qty,
                write_address=7,
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
        self.data_window_length = int(REALTIME_DATA_WINDOW * 60 * 1000 / self.poll_interval)

        # Слово состояния дискретных сигналов от ПЛК
        self.in_status = 0
        # данные от датчика угла поворота, в градусах
        self.angle_data = np.zeros(self.data_window_length, dtype=np.int32)
        # Данные от датчика угла поворота (преобразованные, в градусах)
        self.angle_data_c = np.zeros(self.data_window_length, dtype=np.float16)
        # данные от датчика крутящего момента, в Нм
        self.tension_data = np.zeros(self.data_window_length, dtype=np.int16)
        # Данные от датчика крутящего момента (преобразованные к Нм)
        self.tension_data_c = np.zeros(self.data_window_length, dtype=np.float16)
        # Скорость нарастания момента (моментальные значения в Нм/с)
        self.velocity_data = np.zeros(self.data_window_length, dtype=np.float16)

        # временные метки для потока данных, в мс
        self.times = np.zeros(self.data_window_length, dtype=np.int64)
        self.ptr = 0  # Указатель текущей позиции данных

        # Слово управления для отправки в ПЛК
        self.plc_control_word = 0
        self.write_regs = [0] * 6  # 6 шесть регистров для записи в ПЛК

        # Для обмена по Modbus создаем отдельный поток
        self.worker = Worker(self)
        self.worker_thread = QThread()
        # переносим worker в отдельный поток
        self.worker.moveToThread(self.worker_thread)
        # запускаем worker из главного потока после переноса
        QTimer.singleShot(0, self.worker.start)
        # запускаем поток
        self.worker_thread.start()

        self.time_origin = time.time()  # Начальная временная метка для датасета
        self.prev_time = time.time()

    # Слот вызывается из Worker когда завершено получение новых данных от PLC
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

        # Считываем состояние регистров
        self.in_status = c_short(registers[0]).value

        self.data_updated.emit(registers)

    def get_real_tension(self, registers):
        """Преобразование регистра в значение крутящего момента."""
        tension = 50.0 * float(c_short(registers[1]).value) / 32768.0
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
