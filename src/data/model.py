"""Application model tying command handling and real-time Modbus data.

The module defines :class:`Model`, a central Qt-based object responsible for
coordinating communication with the PLC. It subscribes to updates from
``RealTimeData`` and forwards changes via Qt signals so that other parts of the
application can react.

Модель приложения, объединяющая обработку команд и данные Modbus в реальном времени.

Модуль определяет :class:`Model` — центральный объект на базе Qt, отвечающий за
координацию связи с ПЛК. Он подписывается на обновления от ``RealTimeData`` и
передает изменения через сигналы Qt, чтобы другие части приложения могли реагировать.
"""

from PyQt6.QtCore import QObject, pyqtSignal as Signal, pyqtSlot as Slot

from src.command_handler import CommandHandler
from src.data.realtime_data import RealTimeData


class Model(QObject):
    """Central application model managing Modbus registers and signals.

    The model glues together :class:`RealTimeData` and :class:`CommandHandler`
    while exposing Qt signals when new data arrives or when graphs should be
    refreshed.

    Центральная модель приложения, управляющая регистрами и сигналами Modbus.

    Модель объединяет :class:`RealTimeData` и :class:`CommandHandler`, отправляя
    сигналы Qt при поступлении новых данных или необходимости обновления графиков.
    """

    data_updated = Signal(list)
    graphs_updated = Signal()

    def __init__(self, config, parent=None):
        """Initialize the model.

        Инициализировать модель.

        Args:
            config: Application configuration options.
            parent: Optional QObject parent for Qt ownership.

        Аргументы:
            config: Параметры конфигурации приложения.
            parent: Необязательный родитель QObject для управления владением Qt.
        """
        super(Model, self).__init__(parent)
        self.config = config
        # Данные которые (пишем в/получаем из) регистров Modbus ПЛК с частотой опроса
        self.realtime_data = RealTimeData(self.config, self)
        self.command_handler = CommandHandler(self)

        self.realtime_data.data_updated.connect(self.rt_data_changed)

        # Регистры для записи в ПЛК
        self.modbus_write_regs = {
            'Modbus_CTRL': 0,  # Управление режимом стенда
            'Modbus_TensionSV': 0,  # Задание момента на валу
            'Modbus_VelocitySV': 0,  # Задание скорости сервопривода
            'Modbus_DQ_CTRL': 0,  # Прямое управление дискретными выходами
            'Modbus_UZ_CTRL': 0,  # Прямое управление сервоприводом
            'Modbus_AUX': 0,  # Резерв
        }

    @Slot(list)
    def rt_data_changed(self, registers):
        """Handle updates from real-time data polls.

        Обрабатывать обновления данных опроса в реальном времени.

        Args:
            registers (list): Latest register values retrieved from the PLC.

        Параметры:
            registers (list): Последние значения регистров, полученные от ПЛК.

        Emits:
            data_updated: With the list of updated registers.
            graphs_updated: Notification that graph data has changed.

        Сигналы:
            data_updated: Список обновлённых регистров.
            graphs_updated: Уведомление об изменении данных графиков.
        """
        self.data_updated.emit(registers)
        self.graphs_updated.emit()

