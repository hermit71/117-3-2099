"""Panel containing multiple real-time graphs."""
from __future__ import annotations
from typing import Dict, Optional, Tuple, Union
from PyQt6.QtWidgets import QFrame, QWidget, QVBoxLayout
from PyQt6.QtCore import pyqtSlot as Slot

from src.ui.widgets.graph_widget import GraphWidget
from src.ui.widgets.time_series_plot_widget import TimeSeriesPlotWidget
from src.data.model import RealTimeData

import logging

logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)
# Настройка обработчика для вывода в файл
file_handler = logging.FileHandler('../../117-3-2099.log')
formatter = logging.Formatter('%(name)s %(asctime)s %(levelname)s %(message)s')
file_handler.setFormatter(formatter)
logger.addHandler(file_handler)

X_AXIS_RANGE = 30.0

class PlotPanel(QFrame):
    def __init__(self, parent: QWidget, data_source: Optional[RealTimeData] = None):
        super().__init__(parent)
        self.parent = parent
        self.vbox = QVBoxLayout()
        self.data_source = data_source
        self.plt_torque = TimeSeriesPlotWidget(
            x_window_seconds=X_AXIS_RANGE,
            y_range=(-50.0, 50.0),
            background="w",
            antialias=True,
            with_legend=True,
        )
        self.plt_velocity = TimeSeriesPlotWidget(
            x_window_seconds=X_AXIS_RANGE,
            y_range=(-5.0, 5.0),
            background="w",
            antialias=True,
            with_legend=True,
        )
        self.setup_ui()
        self.plots = [self.plt_torque, self.plt_velocity]

    def setup_ui(self):
        self.vbox.addWidget(self.plt_torque)
        self.vbox.addWidget(self.plt_velocity)
        self.setLayout(self.vbox)

        self.plt_torque.set_axis_labels(y_label="Крутящий момент, Нм")
        self.plt_velocity.set_axis_labels(y_label='Скорость изменения, Нм/с')

    def config(self, data_source: Optional[RealTimeData] = None):
        self.data_source = data_source

    @Slot()
    def update_plots(self):
        if self.data_source is not None:
            torque_data = self.data_source.torque_data_scaled
            torque_data_indx = self.data_source.head
            self.plt_torque.update(torque_data, torque_data_indx)
            # self.plt_velocity.update()
        else:
            logger.info('Ошибка отображенния графиков: отсутствует источник данных')