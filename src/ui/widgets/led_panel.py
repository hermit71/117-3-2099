"""LED widget utilities used across the application."""

import numpy as np
from PyQt6.QtWidgets import (
    QGridLayout,
    QLabel,
    QGroupBox,
    QVBoxLayout,
    QWidget,
)
from PyQt6.QtCore import Qt, pyqtSlot as Slot
from pyqt_led import Led


class AppLed(Led):
    """LED widget with predefined colors and style."""

    black = np.array([0x00, 0x00, 0x00], dtype=np.uint8)
    white = np.array([0xff, 0xff, 0xff], dtype=np.uint8)
    blue = np.array([0x73, 0xce, 0xf4], dtype=np.uint8)
    green = np.array([0x00, 0xff, 0x00], dtype=np.uint8)
    orange = np.array([0xff, 0xa5, 0x00], dtype=np.uint8)
    purple = np.array([0xaf, 0x00, 0xff], dtype=np.uint8)
    red = np.array([0xff, 0x00, 0x00], dtype=np.uint8)
    yellow = np.array([0xff, 0xff, 0x00], dtype=np.uint8)

    def __init__(self, parent=None):
        super().__init__(parent)
        self._qss = (
            "QPushButton {{ "
            "border: 1px solid lightgray; "
            "border-radius: {}px; "
            "background-color: "
            "    QLinearGradient( "
            "        y1: 0, y2: 1, "
            "        stop: 0 white, "
            "        stop: 0.2 #{}, "
            "        stop: 0.8 #{}, "
            "        stop: 1 #{} "
            "    ); "
            "}}"
        )



class LedPanel(QWidget):
    """Panel containing multiple LED indicators."""

    def __init__(
        self,
        led_number=8,
        size=(12, 12),
        title="Title",
        labels=None,
        parent=None,
    ):
        super().__init__(parent)

        self._title = title
        self._led_number = led_number
        self._shape = AppLed.rectangle
        self._on_color = AppLed.green
        self._off_color = AppLed.black

        self._layout = QVBoxLayout()
        self._grid = QGridLayout()
        self._grid.setColumnStretch(1, 10)

        self.container = QGroupBox(self._title)
        self.leds_ = [AppLed() for _ in range(led_number)]
        self.labels_ = [QLabel() for _ in range(led_number)]
        for i, led in enumerate(self.leds_):
            led.setEnabled(True)
            led.set_shape(self._shape)
            led.set_on_color(self._on_color)
            led.set_off_color(self._off_color)
            led.setFixedSize(size[0], size[1])
            led.setFocusPolicy(Qt.FocusPolicy.NoFocus)
            self._grid.addWidget(led, i, 0, Qt.AlignmentFlag.AlignLeft)
            self._grid.addWidget(self.labels_[i], i, 1, Qt.AlignmentFlag.AlignLeft)

        if labels:
            self.set_labels(labels)

        self.container.setLayout(self._grid)
        self._layout.addWidget(self.container)
        self.setLayout(self._layout)

    def set_label(self, indx, txt):
        """Set text for a specific LED label."""
        self.labels_[indx].setText(txt)

    def set_labels(self, labels):
        """Set texts for all LED labels."""
        for i, label in enumerate(labels):
            self.labels_[i].setText(label)

    def set_led_color(self, indx, on_color, off_color):
        """Configure colors for a single LED."""
        self.leds_[indx].set_on_color(on_color)
        self.leds_[indx].set_off_color(off_color)

    def set_status(self, word, bits):
        """Update LEDs based on bit mask."""
        for i in range(self._led_number):
            self.leds_[i].set_status(1 & (word >> bits[i]))

    @Slot(int)
    def update_view(self, data, bits):
        """Qt slot to update LEDs when data changes."""
        self.set_status(data, bits)