import pyqtgraph as pg

class GraphWidget(pg.PlotWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.parent = parent
        self.x_view_range = {'start': 0, 'end': self.parent.time_window} # Диапазон оси X графика (в единицах времени)
        self.x_view_range_ms = {'start': 0, 'end': (1000* self.parent.time_window)}
        self.x_data_range = {'start': 0, 'end': 0}  # Диапазон данных для отображения
        self.setBackground('#FEFEFA')
        self.base_pen = pg.mkPen(color="#1C1CF0", width=2)
        self.setXRange(self.x_view_range_ms['start'], self.x_view_range_ms['end'])
        self.getPlotItem().setLabel('bottom', 'мс')

        self.showGrid(x=True, y=True)
        self.curve = self.plot(pen=self.base_pen)


    def update_plot(self, dataset_name):
        model = self.parent.model
        if not model: return
        ds = model.realtime_data.get_dataset_by_name(dataset_name)
        start_indx = max(0, (model.realtime_data.ptr - (self.parent.time_window * 40 + 100)))
        time_data = model.realtime_data.times[start_indx:model.realtime_data.ptr]
        value_data = ds[start_indx:model.realtime_data.ptr]
        self.curve.setData(time_data, value_data)

        if model.realtime_data.times[model.realtime_data.ptr-1] > self.x_view_range_ms['end']:
            poll_interval = model.realtime_data.poll_interval
            self.x_view_range_ms['start'] += poll_interval
            self.x_view_range_ms['end'] += poll_interval
            self.setXRange(self.x_view_range_ms['start'], self.x_view_range_ms['end'])
