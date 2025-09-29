"""Widget for displaying a numeric value with a title."""

from PyQt6.QtCore import Qt, QSize, pyqtSlot as Slot
from PyQt6.QtWidgets import QFrame, QVBoxLayout, QLabel, QSizePolicy
from PyQt6.QtGui import QFont
from pyqtgraph import ValueLabel


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
