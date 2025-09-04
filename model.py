import sys

import numpy as np
from PyQt6.QtCore import QTimer, QObject, pyqtSignal as Signal, pyqtSlot as Slot

from command_handler import CommandHandler
from realtime_data import RealTimeData

class Model(QObject):
    data_updated = Signal(list)
    graphs_updated = Signal()

    def __init__(self, parent=None):
        super(Model, self).__init__(parent)
        self.realtime_data = RealTimeData(self)
        self.command_handler = CommandHandler(self)

        self.realtime_data.data_updated.connect(self.rt_data_changed)

        # Регистры для записи в ПЛК
        self.modbus_write_regs = {
            'Modbus_CTRL': 0,             # Команда управления режимами работы стенда
            'Modbus_TensionSV': 0,        # Задание момента на валу
            'Modbus_VelocitySV': 0,       # Задание скорости сервопривода
            'Modbus_DQ_CTRL': 0,          # Команда прямого управления дискретными выходами
            'Modbus_UZ_CTRL': 0,          # Команда прямого управления сервоприводом
            'Modbus_AUX': 0               # Резерв
        }


    @Slot(list)
    def rt_data_changed(self, registers):
        self.data_updated.emit(registers)
        self.graphs_updated.emit()