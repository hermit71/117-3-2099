import numpy as np
from PyQt6.QtWidgets import QFrame, QVBoxLayout, QSpacerItem, QSizePolicy, QGridLayout, QLabel, QGroupBox
from PyQt6.QtCore import Qt, pyqtSignal as Signal, pyqtSlot as Slot

from src.ui.widgets.led_panel import (LedPanel)

class LedDashboardPanel(QFrame):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.model = None
        self.led_dashboards = None
        self.vbox = QVBoxLayout()

    def config(self, model=None, led_dashboards=None):
        self.model = model
        self.led_dashboards = led_dashboards
        self.setupUI()
        self.model.data_updated.connect(self.data_update)

    def setupUI(self):
        if self.led_dashboards is None:
            print('No led_dashboards defined')
            return
        else:
            for i, ld in enumerate(self.led_dashboards):
                led_p = LedPanel(led_number=ld[1]['num'], title=ld[1]['title'], labels=ld[1]['labels'])
                self.led_dashboards[i].append(led_p)    # Добавляем в список led панелей созданный экземпляр панели
                self.vbox.addWidget(led_p)
            spacerItem = QSpacerItem(20, 40, QSizePolicy.Policy.Minimum, QSizePolicy.Policy.Expanding)
            self.vbox.addItem(spacerItem)
            self.setLayout(self.vbox)


    @Slot(list)
    def data_update(self, registers):
        for i, ld in enumerate(self.led_dashboards):
            ld[2].update_view(
                registers[ld[1]['register']],   # Обновляем состояние led панели в соответствии с нужным регистром Modbus
                ld[1]['bits'])                  # и нужными битами этого регистра