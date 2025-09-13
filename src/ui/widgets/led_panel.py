"""LED indicator widgets used throughout the UI."""

import numpy as np
from PyQt6.QtCore import Qt, pyqtSlot as Slot
from PyQt6.QtWidgets import QWidget, QVBoxLayout, QGridLayout, QGroupBox, QLabel
from pyqt_led import Led


class AppLed(Led):
    """Styled LED widget with predefined colors."""

    black = np.array([0x00, 0x00, 0x00], dtype=np.uint8)
    white = np.array([0xFF, 0xFF, 0xFF], dtype=np.uint8)
    blue = np.array([0x73, 0xCE, 0xF4], dtype=np.uint8)
    green = np.array([0x00, 0xFF, 0x00], dtype=np.uint8)
    orange = np.array([0xFF, 0xA5, 0x00], dtype=np.uint8)
    purple = np.array([0xAF, 0x00, 0xFF], dtype=np.uint8)
    red = np.array([0xFF, 0x00, 0x00], dtype=np.uint8)
    yellow = np.array([0xFF, 0xFF, 0x00], dtype=np.uint8)

    def __init__(self, parent=None):
        super().__init__(parent)
        self._qss = (
            "QPushButton {{ "
            "border: 1px solid lightgray; "
            "border-radius: {}px; "
            "background-color: "
            "   QLinearGradient("
            "       y1: 0, y2: 1, "
            "       stop: 0 white, "
            "       stop: 0.2 #{}, "
            "       stop: 0.8 #{}, "
            "       stop: 1 #{} "
            "   ); "
            "}}"
        )


class LedPanel(QWidget):
    """Panel containing a group of LEDs with optional labels."""

    def __init__(
        self,
        led_number=8,
        size=(12, 12),
        title='Title',
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
        """Set text for a specific label."""
        self.labels_[indx].setText(txt)

    def set_labels(self, labels):
        """Apply a list of label texts."""
        for i, label in enumerate(labels):
            self.labels_[i].setText(label)

    def set_led_color(self, indx, on_color, off_color):
        """Configure on/off colors for a specific LED."""
        self.leds_[indx].set_on_color(on_color)
        self.leds_[indx].set_off_color(off_color)

    def set_status(self, word, bits):
        """Update LED statuses from bit masks."""
        for i in range(self._led_number):
            self.leds_[i].set_status(1 & (word >> bits[i]))

    @Slot(int)
    def update_view(self, data, bits):
        """Slot to update LEDs from Modbus data."""
        self.set_status(data, bits)

