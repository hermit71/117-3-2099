from PyQt6.QtCore import Qt, QSize, pyqtSignal as Signal, pyqtSlot as Slot
from PyQt6.QtWidgets import QFrame, QVBoxLayout, QLabel, QSizePolicy
from PyQt6.QtGui import QFont
from pyqtgraph import ValueLabel


class valueWidget(QFrame):
    def __init__(self, parent=None, title='', data_source=None):
        super(valueWidget, self).__init__(parent)
        self.parent = parent
        self.label = QLabel(title)
        self.value = ValueLabel(averageTime=0.5) # QLabel(self)
        self.data_source = data_source
        self.vbox = QVBoxLayout(self)
        self.vbox.addWidget(self.label)
        self.vbox.addWidget(self.value)
        self.setLayout(self.vbox)
        self.setupUI()

    def setupUI(self):
        # Фрейм
        sizePolicy = QSizePolicy(QSizePolicy.Policy.Minimum, QSizePolicy.Policy.Preferred)
        self.setSizePolicy(sizePolicy)
        self.setMinimumSize(QSize(180, 0))
        self.setFrameShape(QFrame.Shape.StyledPanel)
        self.setFrameShadow(QFrame.Shadow.Plain)
        self.vbox.setContentsMargins(0, 0, 0, 0)
        self.vbox.setSpacing(0)
        self.vbox.setStretch(0, 10)
        self.vbox.setStretch(1, 16)

        # Текст надписи виджета
        self.label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        font = QFont()
        font.setFamily("Segoe UI")
        font.setPointSize(10)
        self.label.setFont(font)
        self.label.setStyleSheet("background-color: rgb(0, 85, 127);\n"
                                    "color: rgb(255, 255, 255);")

        # Поле значения величины
        self.value.setAlignment(Qt.AlignmentFlag.AlignCenter)
        font = QFont()
        font.setFamily("Inconsolata LGC Nerd Font")
        font.setPointSize(16)
        #font.setBold(False)
        self.value.setFont(font)
        self.value.setStyleSheet("color: rgb(0, 85, 127);")
        self.value.formatStr = '{avgValue:0.2f}'

    @Slot()
    def update(self):
        indx = self.parent.model.realtime_data.ptr - 1
        value = self.data_source[indx]
        self.value.setValue(value)
        #self.value.setText(f'{value:.2f}')