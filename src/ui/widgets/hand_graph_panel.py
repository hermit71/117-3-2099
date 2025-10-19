"""Panel containing multiple real-time graphs."""

from PyQt6.QtWidgets import QFrame, QWidget, QVBoxLayout
from PyQt6.QtCore import pyqtSlot as Slot

from src.ui.widgets.graph_widget import GraphWidget
from src.ui.widgets.time_series_plot_widget import TimeSeriesPlotWidget

X_AXIS_RANGE = 30.0
POINTS_PER_WINDOW = 1200

class PlotPanel(QFrame):
    def __init__(self, parent: QWidget, data_source):
        super().__init__(parent)
        self.parent = parent
        self.vbox = QVBoxLayout()
        self.data_source = data_source
        self.plt_torque = TimeSeriesPlotWidget(
        x_window_seconds=X_AXIS_RANGE,
        points_per_window=POINTS_PER_WINDOW,
        y_range=(-50.0, 50.0),
        background="w",
        antialias=True,
        with_legend=True,
        )
        self.plt_velocity = TimeSeriesPlotWidget(
            x_window_seconds=X_AXIS_RANGE,
            points_per_window=POINTS_PER_WINDOW,
            y_range=(-5.0, 5.0),
            background="w",
            antialias=True,
            with_legend=True,
        )
        self.setup_ui()

    def setup_ui(self):
        self.vbox.addWidget(self.plt_torque)
        self.vbox.addWidget(self.plt_velocity)
        self.setLayout(self.vbox)

        self.plt_torque.set_axis_labels(y_label="Крутящий момент, Нм")
        self.plt_velocity.set_axis_labels(y_label='Скорость изменения, Нм/с')


class HandGraphPanel(QFrame):
    """Widget arranging and updating graph widgets."""
    def __init__(self, parent=None):
        super().__init__(parent)
        self.model = None
        self.plots_description = None
        self.plots = None
        self.display_points = 2000
        self.time_window = 30  # seconds

    def _get_graph_widgets(self):
        """Return child widgets that are ``GraphWidget`` instances."""
        return [child for child in self.children() if isinstance(child, GraphWidget)]

    def graph_config(self, model, plots_description):
        """Configure graphs and connect model signals."""
        self.model = model
        self.plots_description = plots_description
        self.plots = self._get_graph_widgets()
        for i, plot in enumerate(self.plots):
            desc = self.plots_description[i][1]
            plot.apply_style(
                line_color=desc['line_color'],
                background=desc['background'],
                grid_color=desc['grid_color'],
                line_width=desc['line_width'],
            )
            plot.setLimits(
                yMin=desc['y_limits'][0],
                yMax=desc['y_limits'][1],
                minYRange=desc['y_limits'][0],
                maxYRange=desc['y_limits'][1],
            )
        if self.model:
            self.model.data_updated.connect(self.update_plots)

        for i in range(1, len(self.plots)):
            self.plots[i].setXLink(self.plots[0])

    @Slot(list)
    def update_plots(self, registers):
        """Update plots with new data from the model."""
        for i, plot in enumerate(self.plots):
            plot.update_plot(self.plots_description[i][1]['dataset_name'])
