from PyQt6.QtWidgets import QWidget, QVBoxLayout, QSpacerItem, QSizePolicy, QGridLayout, QLabel, QGroupBox, QStatusBar, \
    QHBoxLayout
from PyQt6.QtCore import Qt, pyqtSignal as Signal, pyqtSlot as Slot
from led_panel import appLed

class connectionControl(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent=parent)
        self.status_text = ''
        self.controlLed = appLed()
        self.status = QLabel(f'{self.status_text}')
        self.hbox = QHBoxLayout()
        self.hbox.addWidget(self.controlLed)
        self.hbox.addWidget(self.status)
        self.setLayout(self.hbox)
        self.setupUI()


    def setupUI(self):
        self.controlLed.setEnabled(True)
        self.controlLed.set_shape(appLed.circle)
        self.controlLed.set_on_color(appLed.green)
        self.controlLed.set_off_color(appLed.red)
        self.controlLed.setFixedSize(12, 12)
        self.controlLed.setFocusPolicy(Qt.FocusPolicy.NoFocus)

    @Slot(bool)
    def setStatus(self, status):
        if status:
            self.controlLed.turn_on()
            self.status_text = 'Соединение установлено'
        else:
            self.controlLed.turn_off()
            self.status_text = 'Соединение отсутствует'

