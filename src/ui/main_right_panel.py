from PyQt6.QtWidgets import QFrame, QVBoxLayout, QSpacerItem, QSizePolicy
from PyQt6.QtCore import pyqtSlot as Slot

from src.ui.widgets.led_panel import LedPanel


class MainRightPanel(QFrame):
    """Main panel on the right side displaying LED dashboards."""

    def __init__(self, parent=None):
        """Initialize empty right panel."""
        super().__init__(parent)
        self.model = None
        self.led_dashboards = None
        self.vbox = QVBoxLayout()

    def config(self, model=None, led_dashboards=None):
        """Configure panel with model and dashboards."""
        self.model = model
        self.led_dashboards = led_dashboards
        self.setup_ui()
        self.signal_connections()

    def signal_connections(self):
        """Connect signals to slots."""
        pass

    def setup_ui(self):
        """Create LED dashboard widgets."""
        if self.led_dashboards is None:
            print('No led_dashboards defined')
            return
        else:
            for i, ld in enumerate(self.led_dashboards):
                led_p = LedPanel(led_number=ld[1]['num'], title=ld[1]['title'], labels=ld[1]['labels'])
                self.vbox.addWidget(led_p)
            spacerItem = QSpacerItem(20, 40, QSizePolicy.Policy.Minimum, QSizePolicy.Policy.Expanding)
            self.vbox.addItem(spacerItem)
            self.setLayout(self.vbox)

    @Slot(list)
    def data_update(self, registers):
        """Placeholder for reacting to data updates."""
        pass
