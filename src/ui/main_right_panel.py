"""Right panel containing LED dashboards."""

import logging

from PyQt6.QtWidgets import QFrame, QSpacerItem, QSizePolicy, QVBoxLayout
from PyQt6.QtCore import pyqtSlot as Slot

from src.ui.widgets.led_panel import LedPanel

logger = logging.getLogger(__name__)

class MainRightPanel(QFrame):
    """Main right panel with LED dashboards."""

    def __init__(self, parent=None):
        super().__init__(parent)
        self.model = None
        self.led_dashboards = None
        self.vbox = QVBoxLayout()

    def config(self, model=None, led_dashboards=None):
        """Configure panel with a model and dashboards."""
        self.model = model
        self.led_dashboards = led_dashboards
        self.setup_ui()
        self.signal_connections()

    def signal_connections(self):
        """Connect signals for panel widgets."""
        pass

    def setup_ui(self):
        """Create LED dashboards and layout."""
        if self.led_dashboards is None:
            logger.info("No led_dashboards defined")
            return
        for ld in self.led_dashboards:
            led_p = LedPanel(
                led_number=ld[1]["num"],
                title=ld[1]["title"],
                labels=ld[1]["labels"],
            )
            self.vbox.addWidget(led_p)
        spacer_item = QSpacerItem(
            20, 40, QSizePolicy.Policy.Minimum, QSizePolicy.Policy.Expanding
        )
        self.vbox.addItem(spacer_item)
        self.setLayout(self.vbox)

    @Slot(list)
    def data_update(self, registers):
        """Handle data updates from the model."""
        pass