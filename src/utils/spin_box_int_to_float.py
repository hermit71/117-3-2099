from PyQt6.QtWidgets import QDoubleSpinBox
from PyQt6.QtCore import Qt, QSize, pyqtSignal as Signal, pyqtSlot as Slot


class appSpinBox(QDoubleSpinBox):
    def __init__(self, parent=None):
        super(appSpinBox, self).__init__(parent)

    @Slot(int)
    def update(self, value):
        v = self.base_round(value, 5)

        s = float(v) / 10.0
        self.setValue(s)

    def base_round(self, x, base=5):
        return base * round(x / base)
