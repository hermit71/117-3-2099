from PyQt6.QtWidgets import QFrame, QHBoxLayout, QSpacerItem, QSizePolicy, QPushButton
from PyQt6.QtCore import Qt, pyqtSignal as Signal, pyqtSlot as Slot, QSize
from src.ui.widgets.dashboard_value_widget import valueWidget

class dashboardPanel(QFrame):
    def __init__(self, parent=None, model=None):
        super(dashboardPanel, self).__init__(parent)
        self.model = None
        self.valueTension = valueWidget(self, title='Крутящий момент, Нм')
        self.valueVelocity = valueWidget(self, title='Скорость изменения, Нм/с')
        self.valueAngle = valueWidget(self, title='Угол поворота, \u00B0')
        self.hbox = QHBoxLayout()
        self.hbox.addWidget(self.valueTension)
        self.hbox.addWidget(self.valueVelocity)
        self.hbox.addWidget(self.valueAngle)
        self.spacerItem = QSpacerItem(20, 40, QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Minimum)
        self.hbox.addItem(self.spacerItem)
        self.setLayout(self.hbox)
        self.setupUI()

    def setupUI(self):
        pass

    def config(self, model):
        if model:
            self.model = model
            self.valueTension.data_source = self.model.realtime_data.tension_data_c
            self.valueVelocity.data_source = self.model.realtime_data.velocity_data
            self.valueAngle.data_source = self.model.realtime_data.angle_data_c
            self.model.graphs_updated.connect(self.valueTension.update)
            self.model.graphs_updated.connect(self.valueVelocity.update)
            self.model.graphs_updated.connect(self.valueAngle.update)

