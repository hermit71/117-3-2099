"""Widget to display connection status using an LED indicator."""

from PyQt6.QtWidgets import (
    QLabel,
    QHBoxLayout,
    QWidget,
)
from PyQt6.QtCore import Qt, pyqtSlot as Slot

from src.ui.widgets.led_panel import AppLed

class ConnectionControl(QWidget):
    """LED indicator widget showing connection status."""

    def __init__(self, parent=None):
        super().__init__(parent=parent)
        self.status_text = ""
        self.control_led = AppLed()
        self.status = QLabel(f"{self.status_text}")
        self.hbox = QHBoxLayout()
        self.hbox.addWidget(self.control_led)
        self.hbox.addWidget(self.status)
        self.setLayout(self.hbox)
        self.setup_ui()

    def setup_ui(self):
        """Configure LED appearance."""
        self.control_led.setEnabled(True)
        self.control_led.set_shape(AppLed.circle)
        self.control_led.set_on_color(AppLed.green)
        self.control_led.set_off_color(AppLed.red)
        self.control_led.setFixedSize(12, 12)
        self.control_led.setFocusPolicy(Qt.FocusPolicy.NoFocus)

    @Slot(bool)
    def set_status(self, status):
        """Update LED and text based on connection status."""
        if status:
            self.control_led.turn_on()
            self.status_text = "Соединение установлено"
            self.status.setText(self.status_text)
        else:
            self.control_led.turn_off()
            self.status_text = "Соединение отсутствует"
            self.status.setText(self.status_text)

