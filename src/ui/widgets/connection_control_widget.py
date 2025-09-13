"""Widget displaying connection status with an LED indicator."""

from PyQt6.QtWidgets import QWidget, QHBoxLayout, QLabel
from PyQt6.QtCore import Qt, pyqtSlot as Slot

from src.ui.widgets.led_panel import AppLed


class ConnectionControl(QWidget):
    """Small status widget with an LED indicator showing connection state."""

    def __init__(self, parent=None):
        super().__init__(parent)
        self.status_text = ""
        self.control_led = AppLed()
        self.status = QLabel(self.status_text)
        layout = QHBoxLayout(self)
        layout.addWidget(self.control_led)
        layout.addWidget(self.status)
        self.setLayout(layout)
        self._setup_ui()

    def _setup_ui(self):
        """Configure LED appearance."""
        self.control_led.setEnabled(True)
        self.control_led.set_shape(AppLed.circle)
        self.control_led.set_on_color(AppLed.green)
        self.control_led.set_off_color(AppLed.red)
        self.control_led.setFixedSize(12, 12)
        self.control_led.setFocusPolicy(Qt.FocusPolicy.NoFocus)

    @Slot(bool)
    def set_status(self, status):
        """Update LED and text to reflect connection status."""
        if status:
            self.control_led.turn_on()
            self.status_text = "Соединение установлено"
        else:
            self.control_led.turn_off()
            self.status_text = "Соединение отсутствует"
        self.status.setText(self.status_text)

