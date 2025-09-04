import sys
import time
import numpy as np
from PyQt6 import QtWidgets, QtCore
import pyqtgraph as pg
from pymodbus.client import ModbusTcpClient
from pymodbus.exceptions import ModbusException


class RealTimePlot(QtWidgets.QMainWindow):
    def __init__(self):
        super().__init__()
        self.initUI()
        self.initModbus()
        self.initData()
        self.setupTimer()

    def initUI(self):
        # Настройка главного окна
        self.setWindowTitle('Real-Time Modbus Plot')
        self.setGeometry(100, 100, 800, 600)

        # Центральный виджет
        self.central_widget = QtWidgets.QWidget()
        self.setCentralWidget(self.central_widget)
        self.layout = QtWidgets.QVBoxLayout(self.central_widget)

        # Создание графика
        self.plot_widget = pg.PlotWidget()
        self.layout.addWidget(self.plot_widget)

        # Настройка графика
        self.plot_widget.setLabel('left', 'Value')
        self.plot_widget.setLabel('bottom', 'Time', 's')
        self.plot_widget.showGrid(x=True, y=True)
        self.curve = self.plot_widget.plot(pen='y')

        # Виджет для настройки временного окна
        self.time_range_combo = QtWidgets.QComboBox()
        self.time_range_combo.addItems(['5 s', '30 s', '60 s', '180 s'])
        self.time_range_combo.currentTextChanged.connect(self.updateTimeRange)
        self.layout.addWidget(self.time_range_combo)

        self.time_range = 5  # Начальное значение временного окна в секундах

    def initModbus(self):
        # Настройка Modbus клиента
        self.client = ModbusTcpClient('192.168.1.100')  # Укажите IP-адрес PLC
        self.register_address = 0  # Укажите адрес регистра
        self.connected = False
        try:
            self.connected = self.client.connect()
        except ModbusException as e:
            print(f"Modbus connection error: {e}")

    def initData(self):
        # Инициализация массивов данных
        self.max_points = int(180 / 0.1)  # Максимум 3 минуты при 100 мс
        self.times = np.zeros(self.max_points)
        self.values = np.zeros(self.max_points)
        self.ptr = 0  # Указатель текущей позиции данных
        self.start_time = time.time()

    def setupTimer(self):
        # Настройка таймера для обновления данных (100 мс)
        self.timer = QtCore.QTimer()
        self.timer.timeout.connect(self.update)
        self.timer.start(100)  # 100 мс

    def updateTimeRange(self, text):
        # Обновление временного окна
        self.time_range = float(text.split()[0])
        self.plot_widget.setXRange(-self.time_range, 0)

    def update(self):
        if not self.connected:
            return

        try:
            # Чтение данных из регистра
            result = self.client.read_holding_registers(self.register_address, 1)
            if result.isError():
                print("Error reading register")
                return
            value = result.registers[0]

            # Обновление данных
            current_time = time.time() - self.start_time
            self.times[self.ptr] = current_time
            self.values[self.ptr] = value
            self.ptr += 1

            # Если массив заполнен, сдвигаем данные
            if self.ptr >= self.max_points:
                self.times[:-1] = self.times[1:]
                self.values[:-1] = self.values[1:]
                self.ptr = self.max_points - 1

            # Обновление графика
            display_points = int(self.time_range / 0.1)
            start_idx = max(0, self.ptr - display_points)
            time_data = self.times[start_idx:self.ptr] - current_time
            value_data = self.values[start_idx:self.ptr]
            self.curve.setData(time_data, value_data)

        except ModbusException as e:
            print(f"Modbus error: {e}")

    def closeEvent(self, event):
        # Закрытие соединения при выходе
        if self.connected:
            self.client.close()


def main():
    app = QtWidgets.QApplication(sys.argv)
    window = RealTimePlot()
    window.show()
    sys.exit(app.exec())


if __name__ == '__main__':
    main()