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
        self.update_time = 250 # ms

        self.label = QLabel(self.title)
        self.value = ValueLabel(averageTime=self.average_time)
        self.vbox = QVBoxLayout(self)
        self.vbox.addWidget(self.label)
        self.vbox.addWidget(self.value)
        self.setLayout(self.vbox)
        self._setup_ui()
        self.timer = QTimer()
        self.timer.timeout.connect(self.on_timer)
        self.timer.start(self.update_time)

    def _setup_ui(self):
        """Configure layout and label styles."""
        size_policy = QSizePolicy(
            QSizePolicy.Policy.Fixed, QSizePolicy.Policy.Fixed
        )
        self.setSizePolicy(size_policy)
        self.setFixedSize(QSize(150,75))
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

    def _set_data_source(self, data_source):
        self.data_source = data_source

    def _set_title(self, title):
        self.title = title
        self.label.setText(title)

    def _apply_style(self, style):
        self.style = style

    def _set_average_time(self, average_time):
        self.average_time = average_time
        self.value.setAverageTime(average_time)

    @Slot()
    def on_timer(self):
        if self.data_source is None:
            self.value.setValue(0.0)
        else:
            self.value.setValue(self.data_source())

class ValueWidget(QFrame):
    """Widget combining a label and a live numeric value."""

    def __init__(self, parent=None, title="", data_source=""):
        super().__init__(parent)
        self.parent = parent
        self.label = QLabel(title)
        self.value = ValueLabel(averageTime=0.5)
        self.data_source = data_source
        self.vbox = QVBoxLayout(self)
        self.vbox.addWidget(self.label)
        self.vbox.addWidget(self.value)
        self.setLayout(self.vbox)
        self._setup_ui()

    def _setup_ui(self):
        """Configure layout and label styles."""
        size_policy = QSizePolicy(
            QSizePolicy.Policy.Minimum, QSizePolicy.Policy.Preferred
        )
        self.setSizePolicy(size_policy)
        self.setMinimumSize(QSize(180, 0))
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

    @Slot()
    def update(self):
        """Fetch data from source and update value display."""
        #indx = self.parent.model.realtime_data.ptr - 1
        if self.data_source == "tension":
            value = self.parent.model.realtime_data.tension
        elif self.data_source == "velocity":
            value = self.parent.model.realtime_data.velocity
        elif self.data_source == "angle":
            value = self.parent.model.realtime_data.angle
        else:
            value = 0.0
        self.value.setValue(value)
