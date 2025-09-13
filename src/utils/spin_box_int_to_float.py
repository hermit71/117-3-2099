"""Spin box converting integer input to float representation."""

from PyQt6.QtWidgets import QDoubleSpinBox
from PyQt6.QtCore import pyqtSlot as Slot


class AppSpinBox(QDoubleSpinBox):
    """Spin box that rounds and scales integer values to floats."""

    @Slot(int)
    def update(self, value):
        """Slot to update the displayed value."""
        v = self.base_round(value, 5)
        s = float(v) / 10.0
        self.setValue(s)

    def base_round(self, x, base=5):
        """Round ``x`` to the nearest multiple of ``base``."""
        return base * round(x / base)

