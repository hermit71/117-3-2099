import pyqtgraph as pg
from pyqtgraph import PlotWidget
from PyQt6.QtGui import QFont
from PyQt6.QtCore import pyqtSlot as Slot, pyqtSignal as Signal
from datetime import datetime, timedelta

class AdaptiveGraphic(PlotWidget):
    """Plot widget for visualizing multiple data series with optional axes."""

    mouse_moved_on_plot = Signal(object)

    def __init__(self, parent=None):
        """Initialize the widget with default plot configuration."""
        super().__init__(parent)
        self.plots = [None] * 6
        self.plots_mask = [1, 0, 0, 1, 0, 0]
        self.setBackground('w')
        self.showGrid(x=True, y=True)
        self.context = 'force'
        self.local_plot_data = None
        self.local_x_data = None
        self.initial_graphics_settings()
        self.connect_signals_slots()

    def initial_graphics_settings(self):
        """Set up initial plot appearance and elements."""
        self.p_range = [0, 100]
        self.f_range = [-1000, 1000]
        self.t_range = [20, 60]
        self._plot_pens_define()
        self._axis_styles_define()
        self._set_labels()
        self._set_datetime_axis()
        self._set_proxy()
        self._add_line()
        self._add_plots()
        self.view_box = self.getPlotItem().vb
        self.view_box.setMouseEnabled(x=True, y=False)
        self.view_box.setBorder(self.plot_border_main)
        self.setMenuEnabled(False)
        self._set_plot_context(self.context)

    def connect_signals_slots(self):
        """Connect internal signals and slots."""
        self.getViewBox().sigResized.connect(self._update_views)

    def set_plot_mask(self, mask):
        """Set plot visibility mask."""
        self.plots_mask = mask

    def _add_plots(self):
        for i, v_ in enumerate(self.plots_mask):
            self.plots[i] = pg.PlotCurveItem(pen=self.plot_pens[i])
            self.addItem(self.plots[i])
        self._plots_control(self.plots_mask)

    def _plots_control(self, mask):
        for i, v_ in enumerate(mask):
            if v_:
                self.plots[i].show()
            else:
                self.plots[i].hide()

    def _set_labels(self):
        self.setLabel('right', 'Температура (С)', **self._styles_right_axis)

    def _plot_pens_define(self):
        # Стили графиков
        self.plot_pens = [None] * 6
        self.plot_pens[0] = pg.mkPen(color='#ff0000', width=2) # Температура
        self.plot_pens[1] = pg.mkPen(color='#9575f4', width=2)  # Давление в системе
        self.plot_pens[2] = pg.mkPen(color='#006393', width=2)  # Давление над пакером
        self.plot_pens[3] = pg.mkPen(color='#009f80', width=2)  # Двление в пакере
        self.plot_pens[4] = pg.mkPen(color='#d76b00', width=2)  # Давление под пакером
        self.plot_pens[5] = pg.mkPen(color='#804040', width=2)  # Усилие на пакере

        self.plot_border_main = pg.mkPen(color='#808080', width=1)
        self.crosshair_pen = pg.mkPen(color='#0000f2', width=0.2)

    def _axis_styles_define(self):
        self._styles_left_axis = {'color': '#025b94', 'font-size': '18px'}
        self._styles_right_axis = {'color': '#ff0000', 'font-size': '18px'}

    def _set_additional_temperature_axis(self):
        self.p2 = pg.ViewBox()
        self.scene().addItem(self.p2)
        self.getAxis('right').linkToView(self.p2)
        self.getAxis('right').setGrid(False)
        self.p2.setXLink(self)
        self.p2.setYRange(self.t_range[0], self.t_range[1], padding=0.02)
        self.p2.addItem((self.plots[0]))
        self.p2.setMenuEnabled(False)

    def _set_plot_context(self, context):
        match context:
            case 'force':
                self.setYRange(self.f_range[0], self.f_range[1], padding=0.02)
                self.setLabel('left', 'Статический крутящий момент (Н)', **self._styles_left_axis)
        self.p2.setYRange(self.t_range[0], self.t_range[1], padding=0.02)
        self.context = context

    def _set_datetime_axis(self):
        now = datetime.now()
        now_ = datetime.now() + timedelta(minutes=20)
        self.date_axis_temperature = pg.DateAxisItem(orientation='bottom')
        self.date_axis_temperature.setGrid(100)
        self.date_axis_main = pg.DateAxisItem(orientation='bottom')
        self.date_axis_main.setGrid(100)
        self.setAxisItems(axisItems={'bottom': self.date_axis_main})
        self.setXRange(now.timestamp(), now_.timestamp(), padding=0)

    def _set_timing_labels(self):
        txt_font = QFont()
        txt_font.setPixelSize(18)
        self.txt_pd_start = pg.TextItem('Начальное значение: ', anchor=(0, 0), color='#025b94')
        self.txt_pd_end = pg.TextItem('Конечное значение: ', anchor=(0, 0), color='#025b94')
        self.scene().addItem(self.txt_pd_start)
        self.scene().addItem(self.txt_pd_end)
        self.txt_pd_start.setFont(txt_font)
        self.txt_pd_end.setFont((txt_font))
        self.txt_pd_start.setPos(60, 20)
        self.txt_pd_end.setPos(60, 60)

    def _set_proxy(self) -> None:
        """Set Signal Proxy"""
        self.proxy = pg.SignalProxy(self.getPlotItem().scene().sigMouseMoved, rateLimit=60, slot=self.mouse_moved)

    def _add_line(self):
        """Add a line that moves with the cursor"""
        # Since it is hard to see by default, specify the color and width
        self.vertical_line = pg.InfiniteLine(angle=90, movable=False, pen=self.crosshair_pen)
        self.horizontal_line = pg.InfiniteLine(angle=0, movable=False, pen=self.crosshair_pen)
        self.getPlotItem().addItem(self.vertical_line, ignoreBounds=True)
        self.getPlotItem().addItem(self.horizontal_line, ignoreBounds=True)

    def _get_plot_data(self, local_ds):
        request = f'SELECT * FROM local_data'
        data = local_ds.select_data(request)
        return data

    def _get_data_y(self, x):
        data_y = None
        if self.local_x_data:
            _m = [abs(x_ - x) for x_ in self.local_x_data]
            indx = _m.index(min(_m))
            data_y = self.local_plot_data[indx]
        return data_y

    def _update_views(self):
        self.p2.setGeometry(self.getViewBox().sceneBoundingRect())

    def set_x_range(self, t0, t1):
        """Set the visible X-axis range."""
        self.setXRange(t0.timestamp(), t1.timestamp(), padding=0)

    def _update_plot(self, local_ds):
        main_plot_item_range = self.getPlotItem().viewRange()
        t0, t1 = (main_plot_item_range[0][0], main_plot_item_range[0][1])
        instant_now = datetime.now()
        # Двигаем график по времени когда приходят новые данные
        if instant_now.timestamp() >= t1:
            self.setXRange(instant_now.timestamp() - (t1 - t0), instant_now.timestamp(), padding=0)

        # Обновляем графики
        request = f"SELECT * FROM local_data WHERE dt>='{t0}'"
        data = local_ds.select_data(request)
        self.local_plot_data = data
        graph_x = [datetime.strptime(d[1], '%Y-%m-%d %H:%M:%S.%f').timestamp() for d in data]
        self.local_x_data = graph_x
        for i, v_ in enumerate(self.plots_mask):
            if v_:
                self.plots[i].setData(graph_x, [d[i + 2] for d in data])

    def on_sensor_values_changed(self, last_data_row, local_ds):
        """Update plot when new sensor values are available."""
        self.local_ds = local_ds
        self._update_plot(local_ds)

    def on_change_right_axis_visibility(self, state):
        """Toggle visibility of the right axis."""
        if state:
            self.getPlotItem().showAxis('right')
            self.plots_mask[0] = 1
            self.plots[0].show()
        else:
            self.getPlotItem().hideAxis('right')
            self.plots_mask[0] = 0
            self.plots[0].hide()

    def on_visibility_chb(self, num, state):
        """Handle visibility checkbox changes."""
        if state == 2:
            self.plots_mask[num] = 1
            self.plots[num].show()
        elif state == 0:
            self.plots_mask[num] = 0
            self.plots[num].hide()
        if self.plots_mask[-1]:
            self._set_plot_context('force')
        else:
            self._set_plot_context('pressure')


    @Slot(str, float)
    def on_axis_scale_change(self, axis_name, value):
        """Change axis ranges based on provided values."""
        match axis_name:
            case 'p_max':
                self.p_range[1] = value
            case 'p_min':
                self.p_range[0] = value
            case 'f_max':
                self.f_range[1] = value
            case 'f_min':
                self.f_range[0] = value
            case 't_max':
                self.t_range[1] = value
            case 't_min':
                self.t_range[0] = value
        self._set_plot_context(self.context)

    @Slot(tuple)
    def mouse_moved(self, evt):
        """Emit data and move crosshair when mouse moves."""
        pos = evt[0]
        if self.getPlotItem().sceneBoundingRect().contains(pos):
            mouse_point = self.view_box.mapSceneToView(pos)
            x = mouse_point.x()
            self.mouse_moved_on_plot.emit(self._get_data_y(x))
            self.vertical_line.setPos(mouse_point.x())
            self.horizontal_line.setPos(mouse_point.y())
