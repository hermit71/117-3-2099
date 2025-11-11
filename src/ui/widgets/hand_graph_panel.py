"""Panel containing multiple real-time graphs."""

from PyQt6.QtWidgets import QFrame, QWidget, QVBoxLayout
from PyQt6.QtCore import pyqtSlot as Slot

from src.ui.widgets.graph_widget import GraphWidget
from src.ui.widgets.time_series_plot_widget import TimeSeriesPlotWidget

X_AXIS_RANGE = 30.0

class PlotPanel(QFrame):
    def __init__(self, parent: QWidget, data_source=None):
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