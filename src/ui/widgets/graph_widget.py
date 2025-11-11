"""Graph widget for displaying real-time datasets."""

import pyqtgraph as pg


class GraphWidget(pg.PlotWidget):
    """PlotWidget with convenience methods for time-series data."""

    def __init__(self, parent=None):
        super().__init__(parent)
        self.parent = parent
        if self.parent is not None:
            self.config = parent.config
            self.model = parent.model
        else:
            print('GraphWidget has no parent, unable to initialize GraphWidget')
            return
        if self.config is not None:
            # Диапазон оси X графика (в единицах времени)
            self.x_view_range = self.config.get("x_view_range", {'start': 0, 'end': 30})
            self.x_view_range_ms = {
                'start': self.x_view_range['start'],
                'end': self.x_view_range['end'] * 1000
            }
        else:
            print('GraphWidget get no config, unable to initialize GraphWidget')
            return

        # Диапазон данных для отображения
        self.x_data_range = {'start': 0, 'end': 0}

        self.setXRange(self.x_view_range['start'], self.x_view_range['end'])
        self.getPlotItem().setLabel('bottom', 'Время, с')

        # Base curve pen and default styling
        self.base_pen = pg.mkPen(color="#1C1CF0", width=2)

        self.apply_axes_style(self.config.get("base_axes_style", {}))

        self.curve = self.plot(pen=self.base_pen)
        self.apply_style(
            line_color="#1C1CF0",
            background="#FEFEFA",
            grid_color="#C8C8C8",
            line_width=2,
        )

    def apply_style(self, line_color, background, grid_color, line_width):
        """Apply visual style parameters to the graph."""
        self.setBackground(background)
        pen = pg.mkPen(color=line_color, width=line_width)
        self.curve.setPen(pen)
        grid_pen = pg.mkPen(color=grid_color)
        for axis in ("left", "bottom"):
            # AxisItem.setStyle() does not support a ``gridPen`` argument. Instead,
            # the grid color follows the tick pen.  Previously this method used an
            # unsupported ``gridPen`` keyword which caused a NameError at runtime
            # (see issue trace in the task description).  By updating the tick pen
            # we effectively apply the desired colour to both the ticks and the
            # grid lines without triggering errors on newer versions of
            # pyqtgraph.
            self.getPlotItem().getAxis(axis).setTickPen(grid_pen)

    def apply_axes_style(
        self,
        style: dict
    ) -> None:
        """Apply styling for background, axes and grid.

        Parameters
        ----------
        background: str
            Background color of the plot area.
        axis_pen: str
            Color for axis lines.
        tick_pen: str
            Color for ticks and grid lines.
        text_pen: str
            Color for axis text.
        grid_alpha: int, optional
            Opacity (0-255) for grid lines.
        """

        self.setBackground(style['background'])
        plot_item = self.getPlotItem()
        plot_item.showGrid(x=True, y=True, alpha=style['grid_alpha'] / 255.0)
        for axis in ("left", "bottom"):
            axis_item = plot_item.getAxis(axis)
            axis_item.setPen(pg.mkPen(style['axis_pen']))
            axis_item.setTickPen(pg.mkPen(style['tick_pen']))
            axis_item.setTextPen(pg.mkPen(style['text_pen']))


    def update_plot(self, dataset_name):
        """Redraw the graph using the specified dataset."""
        model = self.parent.model
        if not model:
            return
        ds = model.realtime_data._get_dataset_by_name(dataset_name)
        start_indx = max(
            0, model.realtime_data.ptr - (self.parent.time_window * 40 + 100)
        )
        #time_data = model.realtime_data.times[
        #    start_indx:model.realtime_data.ptr
        #]
        # value_data = ds[start_indx:model.realtime_data.ptr]
        value_data = model.realtime_data.get_visible_chunk(dataset_name)
        time_data = [i for i in range(model.config.get('ui', 'max_graph_points', 1000))]
        self.curve.setData(time_data, value_data)

        self.x_view_range_ms['start'] = 0
        self.x_view_range_ms['end'] = model.config.get('ui', 'max_graph_points', 1000)
        self.setXRange(
            self.x_view_range_ms['start'],
            self.x_view_range_ms['end'],
        )

        '''
        if (
            model.realtime_data.times[model.realtime_data.ptr - 1]
            > self.x_view_range_ms['end']
        ):
            poll_interval = model.realtime_data.poll_interval
            self.x_view_range_ms['start'] += poll_interval
            self.x_view_range_ms['end'] += poll_interval
            self.setXRange(
                self.x_view_range_ms['start'],
                self.x_view_range_ms['end'],
            )
        '''