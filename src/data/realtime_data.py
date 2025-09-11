# Обмен данными с оборудованием стенда по ModbusTCP
# Включает в себя данные датчиков, данные состояния оборудования и управляющие команды
# Все данные передаются в едином цикле обмена с периодом установленным в переменной poll_inteval
# Обмен данными с ПЛК стенда в программе управления стендом происходит ТОЛЬКО в данном модуле!
import time

from PyQt6.QtCore import Qt, QThread, QTimer, QObject, pyqtSignal as Signal, pyqtSlot as Slot, QThread
from pymodbus.client import ModbusTcpClient
from pymodbus.exceptions import ModbusException
import numpy as np
from ctypes import *

poll_interval = 25 # мс - период опроса датчиков в мс
poll_interval_s = float(poll_interval) / 1000.0
realtime_data_window = 60 # час - временное окно для хранения данных от датчиков в реальном времени в минутах
data_window_length =  int(realtime_data_window * 60 * 1000/poll_interval)


class Worker(QObject):
    data_received = Signal(list)
    connection_status = Signal(bool)

    def __init__(self, data_set):
        QObject.__init__(self)
        self.data_set = data_set
        print('worker init')
        self.initModbus()
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
        self.timer.start(poll_interval)

    def initModbus(self):
        # Настройка Modbus клиента
        self.client = ModbusTcpClient('192.168.6.31')  # IP-адрес PLC ('127.0.0.1')
        self.register_address = 0  # Начальный адрес регистра для чтения
        self.register_qty = 7 # Количество регистров для чтения

    def safe_modbus_read(self, host, port, address, count=1, unit=1, max_retries=3):
        """
        Безопасное чтение Modbus с обработкой ошибок соединения
        """
        client = None
        self.result = None

        for attempt in range(max_retries):
            try:
                client = ModbusTcpClient('127.0.0.1')

                if not client.connect():
                    raise ConnectionError("Не удалось установить соединение")

                self.get_data()

                if self.result.isNone():
                    raise Exception(f"Ошибка Modbus: {self.result}")

                return {
                    'status': 'успешно',
                    'data': self.result.registers,
                    'connected': True
                }

            except (ConnectionResetError, ConnectionError, OSError) as e:
                print(f"Попытка {attempt + 1}: Ошибка соединения - {e}")

                if attempt == max_retries - 1:
                    return {
                        'status': 'отсутствие соединения',
                        'data': None,
                        'connected': False,
                        'error': str(e)
                    }

                time.sleep(1)  # Пауза перед повторной попыткой

            except Exception as e:
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
                    except:
                        pass

        return {
            'status': 'отсутствие соединения',
            'data': None,
            'connected': False
        }

    @Slot()
    def on_timer(self):
        self.get_data()
        #self.safe_modbus_read("", "", "")

    @Slot()
    def get_data(self):
        try:
            # self.result = self.client.read_holding_registers(self.register_address, count=self.register_qty)
            self.result = self.client.readwrite_registers(
                        read_address= self.register_address,
                        read_count= self.register_qty,
                        write_address= 7,
                        values= self.data_set.write_regs)
            self.data_received.emit(self.result.registers)
        except ModbusException as e:

            print(f"Modbus error: {e}")

class RealTimeData(QObject):
    # arg#1: регистры Модбас (необработанные данные)
    # arg#2: новые данные от датчиков в формате [float, ...]
    data_updated = Signal(list)
    prev_time = 0

    def __init__(self, parent=None):
        super(RealTimeData, self).__init__(parent)
        # Слово состояния дискретных сигналов от ПЛК
        self.in_status = 0
        # данные от датчика угла поворота, в градусах
        self.angle_data = np.zeros(data_window_length, dtype=np.int32)
        # Данные от датчика угла поворота (преобразованные, в градусах)
        self.angle_data_c = np.zeros(data_window_length, dtype=np.float16)
        # данные от датчика крутящего момента, в Нм
        self.tension_data = np.zeros(data_window_length, dtype=np.int16)
        # Данные от датчика крутящего момента (преобразованные к Нм)
        self.tension_data_c = np.zeros(data_window_length, dtype=np.float16)
        # Скорость нарастания момента (моментальные значения в Нм/с)
        self.velocity_data = np.zeros(data_window_length, dtype=np.float16)

        # временные метки для потока данных, в мс
        self.times = np.zeros(data_window_length, dtype=np.int64)
        self.ptr = 0  # Указатель текущей позиции данных

        # Слово управления для отправки в ПЛК
        self.plc_control_word = 0
        self.write_regs = [0] * 6 # 6 шесть регистров для записи в ПЛК

        # Для обмена по Modbus создаем отдельный поток
        self.worker = Worker(self)
        self.worker_thread = QThread()
        # переносим worker в отдельный поток
        self.worker.moveToThread(self.worker_thread)
        # запускаем worker из главного потока после переноса
        QTimer.singleShot(0, self.worker.start)
        # запускаем поток
        self.worker_thread.start()

        self.time_origin = time.time() # Начальная временная метка для датасета
        self.prev_time = time.time()

    # Слот вызывается из Worker когда завершено получение новых данных от PLC
    @Slot(list)
    def update(self, registers):
        # Обновление данных
        self.times[self.ptr] = round((time.time() - self.time_origin) * 1000)
        self.tension_data_c[self.ptr] = self.get_real_tension(registers)
        self.angle_data_c[self.ptr] = self.get_real_angle(registers)
        self.velocity_data[self.ptr] = self.get_real_velocity()
        self.ptr += 1

        # Если массив заполнен, сдвигаем данные
        if self.ptr >= data_window_length:
            self.times[:-1] = self.times[1:]
            self.tension_data_c[:-1] = self.tension_data_c[1:]
            self.angle_data_c[:-1] = self.angle_data_c[1:]
            self.velocity_data[:-1] = self.velocity_data[1:]
            self.ptr = data_window_length - 1

        # Считываем состяние регистров
        self.in_status = c_short(registers[0]).value

        self.data_updated.emit(registers)

    def get_real_tension(self, registers):
        tension = 50.0 * float(c_short(registers[1]).value) / 32768.0
        return tension

    def get_real_angle(self, registers):
        angle = float((registers[3] << 16) | registers[2]) / 768.0
        return angle

    def get_real_velocity(self):
        velocity = 0.0
        if self.ptr > 0:
            velocity =  (self.tension_data_c[self.ptr] - self.tension_data_c[self.ptr - 1]) / poll_interval_s
        return velocity

    def get_dataset_by_name(self, dataset_name):
        match dataset_name:
            case 'tension_data_c':
                return self.tension_data_c
            case 'angle_data_c':
                return self.angle_data_c
            case 'velocity_data':
                return self.velocity_data
    @Slot(dict)
    def modbus_registers_to_PLC_update(self, regs):
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
