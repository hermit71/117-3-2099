"""Widget for displaying a numeric value with a title."""

from PyQt6.QtCore import Qt, QSize, pyqtSlot as Slot, QTimer
from PyQt6.QtWidgets import QFrame, QVBoxLayout, QLabel, QSizePolicy
from PyQt6.QtGui import QFont
from pyqtgraph import ValueLabel

class ValueDisplay(QFrame):
    def __init__(self, parent=None):
        super(ValueDisplay, self).__init__(parent)
        self.data_source = None
        self.title = 'Title'
        self.style = {}
        self.average_time = 0.5

        self.label = QLabel(self.title)
        self.value = ValueLabel(averageTime=self.average_time)
        self.vbox = QVBoxLayout(self)
        self.vbox.addWidget(self.label)
        self.vbox.addWidget(self.value)
        self.setLayout(self.vbox)
        self._setup_ui()

    def _setup_ui(self):
        """Configure layout and label styles."""
        size_policy = QSizePolicy(
            QSizePolicy.Policy.Fixed, QSizePolicy.Policy.Fixed
        )
        self.setSizePolicy(size_policy)
        self.setFixedSize(QSize(175,72))
        self.setFrameShape(QFrame.Shape.StyledPanel)
        self.setFrameShadow(QFrame.Shadow.Plain)
        self.vbox.setContentsMargins(0, 0, 0, 0)
        self.vbox.setSpacing(0)
        self.vbox.setStretch(0, 10)
        self.vbox.setStretch(1, 16)

        self.label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        font = QFont()
        font.setFamily("Segoe UI")
        font.setPointSize(10)
        self.label.setFont(font)
        self.label.setStyleSheet(
            "background-color: rgb(0, 85, 127);\n" "color: rgb(255, 255, 255);"
        )

        self.value.setAlignment(Qt.AlignmentFlag.AlignCenter)
        font = QFont()
        font.setFamily("Inconsolata LGC Nerd Font")
        font.setPointSize(16)
        self.value.setFont(font)
        self.value.setStyleSheet("color: rgb(0, 85, 127);")
        self.value.formatStr = "{avgValue:0.2f}"

    def set_data_source(self, data_source):
        self.data_source = data_source

    def set_title(self, title):
        self.title = title
        self.label.setText(title)

    def apply_style(self, style):
        self.style = style

    def _set_average_time(self, average_time):
        self.average_time = average_time
        self.value.setAverageTime(average_time)

    @Slot()
    def update(self):
        if self.data_source is None:
            self.value.setValue(0.0)
        else:
            self.value.setValue(self.data_source())
