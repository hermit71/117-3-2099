from PyQt6.QtWidgets import QWidget, QVBoxLayout, QSpacerItem, QSizePolicy, QGridLayout, QLabel, QGroupBox, QStatusBar, \
    QHBoxLayout
from PyQt6.QtCore import Qt, pyqtSignal as Signal, pyqtSlot as Slot
from src.ui.widgets.led_panel import appLed


class connectionControl(QWidget):
    """Widget showing connection status using an LED indicator."""

    def __init__(self, parent=None):
        """Initialize the connection control widget."""
        super().__init__(parent=parent)
        self.status_text = ''
        self.controlLed = appLed()
        self.status = QLabel(f'{self.status_text}')
        self.hbox = QHBoxLayout()
        self.hbox.addWidget(self.controlLed)
        self.hbox.addWidget(self.status)
        self.setLayout(self.hbox)
        self.setup_ui()

    def setup_ui(self):
        """Configure LED and layout properties."""
        self.controlLed.setEnabled(True)
        self.controlLed.set_shape(appLed.circle)
        self.controlLed.set_on_color(appLed.green)
        self.controlLed.set_off_color(appLed.red)
        self.controlLed.setFixedSize(12, 12)
        self.controlLed.setFocusPolicy(Qt.FocusPolicy.NoFocus)

    @Slot(bool)
    def set_status(self, status):
        """Set LED state and status text based on connection."""
        if status:
            self.controlLed.turn_on()
            self.status_text = 'Соединение установлено'
            self.status.setText(self.status_text)
        else:
            self.controlLed.turn_off()
            self.status_text = 'Соединение отсутствует'
            self.status.setText(self.status_text)

