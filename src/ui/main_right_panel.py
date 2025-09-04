from PyQt6.QtWidgets import QFrame, QVBoxLayout, QSpacerItem, QSizePolicy
from PyQt6.QtCore import pyqtSlot as Slot

from src.ui.widgets.led_panel import LedPanel

class MainRightPanel(QFrame):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.model = None
        self.led_dashboards = None
        self.vbox = QVBoxLayout()

    def config(self, model=None, led_dashboards=None):
        self.model = model
        self.led_dashboards = led_dashboards
        self.setupUI()
        self.signal_connections()

    def signal_connections(self):
        pass

    def setupUI(self):

        if self.led_dashboards is None:
            print('No led_dashboards defined')
            return
        else:
            for i, ld in enumerate(self.led_dashboards):
                led_p = LedPanel(led_number=ld[1]['num'], title=ld[1]['title'], labels=ld[1]['labels'])
                self.vbox.addWidget(led_p)
            spacerItem = QSpacerItem(20, 40, QSizePolicy.Policy.Minimum, QSizePolicy.Policy.Expanding)
            self.vbox.addItem(spacerItem)
            self.setLayout(self.vbox)


    @Slot(list)
    def data_update(self, registers):
        pass