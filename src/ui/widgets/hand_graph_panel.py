from PyQt6.QtWidgets import QFrame
from PyQt6.QtCore import Qt, pyqtSignal as Signal, pyqtSlot as Slot
from graph_widget import GraphWidget

class HandGraphPanel(QFrame):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.model = None
        self.plots_description = None
        self.plots = None
        self.display_points = 2000
        self.time_window = 30 # сек - исходный размер окна для отображения на графике

    def get_graph_widgets(self):
        children = self.children()
        widgets = []
        for child in children:
            if isinstance(child, GraphWidget):
                widgets.append(child)
        return widgets

    def graph_config(self, model, plots_description):
        self.model = model
        self.plots_description = plots_description
        self.plots = self.get_graph_widgets()
        for i, plot in enumerate(self.plots):
            plot.setBackground(self.plots_description[i][1]['background'])
            plot.setLimits(yMin=self.plots_description[i][1]['y_limits'][0],
                           yMax=self.plots_description[i][1]['y_limits'][1],
                           minYRange=self.plots_description[i][1]['y_limits'][0],
                           maxYRange=self.plots_description[i][1]['y_limits'][1])
        self.model.data_updated.connect(self.update_plots)

        for i in range(1, len(self.plots)):
            self.plots[i].setXLink(self.plots[0])

    @Slot(list)
    def update_plots(self, registers):
        for i, plot in enumerate(self.plots):
            plot.update_plot(self.plots_description[i][1]['dataset_name'])
