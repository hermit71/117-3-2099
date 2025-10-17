"""Widget for displaying a numeric value with a title."""

from PyQt6.QtCore import Qt, QSize, pyqtSlot as Slot
from PyQt6.QtWidgets import QFrame, QVBoxLayout, QLabel, QSizePolicy
from pyqtgraph import ValueLabel

# ==========================
# Оформление (QSS стили)
# ==========================
STYLE_SHEET = """
    QLabel#titleLabel {
        color: #ffffff;
        background: #00557f;
        font-size: 10pt;
        font-family: Segoe UI;
    }
    ValueLabel#valueDisplay {
        color: #00557f;
        font-size: 16pt;
        font-family: Inconsolata LGC Nerd Font
    }
"""

class ValueDisplay(QFrame):
    def __init__(self, parent=None):
        super(ValueDisplay, self).__init__(parent)
        self.data_source = None
        self.title = 'Title'
        self.style_sheet = STYLE_SHEET
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

        self.label.setObjectName('titleLabel')
        self.label.setAlignment(Qt.AlignmentFlag.AlignCenter)

        self.value.setObjectName('valueDisplay')
        self.value.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.value.formatStr = "{avgValue:0.2f}"

        self.setStyleSheet(self.style_sheet)

    def set_data_source(self, data_source):
        self.data_source = data_source

    def set_title(self, title):
        self.title = title
        self.label.setText(title)

    def apply_style(self, new_style_sheet):
        self.style_sheet = new_style_sheet
        self.setStyleSheet(self.style_sheet)

    def _set_average_time(self, average_time):
        self.average_time = average_time
        self.value.setAverageTime(average_time)

    @Slot()
    def update(self):
        if self.data_source is None:
            self.value.setValue(0.0)
        else:
            self.value.setValue(self.data_source())
