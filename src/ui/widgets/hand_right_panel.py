"""Panel containing multiple LED dashboards."""

import logging
from PyQt6.QtWidgets import QFrame, QVBoxLayout, QSpacerItem, QSizePolicy
from PyQt6.QtCore import pyqtSlot as Slot

from src.ui.widgets.led_panel import LedPanel

logger = logging.getLogger(__name__)


class LedDashboardPanel(QFrame):
    """Container displaying several LED panels."""

    def __init__(self, parent=None):
        super().__init__(parent)
        self.model = None
        self.led_dashboards = None
        self.vbox = QVBoxLayout()

    def config(self, model=None, led_dashboards=None):
        """Attach model and LED panel descriptors and build UI."""
        self.model = model
        self.led_dashboards = led_dashboards
        self._setup_ui()
        if self.model:
            self.model.data_updated.connect(self.data_update)

    def _setup_ui(self):
        """Create LED panels defined in ``led_dashboards``."""
        if not self.led_dashboards:
            logger.warning("No led_dashboards defined")
            return
        for i, ld in enumerate(self.led_dashboards):
            led_panel = LedPanel(
                led_number=ld[1]['num'],
                title=ld[1]['title'],
                labels=ld[1]['labels'],
            )
            self.led_dashboards[i].append(led_panel)
            self.vbox.addWidget(led_panel)

        spacer_item = QSpacerItem(20, 40, QSizePolicy.Policy.Minimum, QSizePolicy.Policy.Expanding)
        self.vbox.addItem(spacer_item)
        self.setLayout(self.vbox)

    @Slot(list)
    def data_update(self, registers):
        """Refresh LED panels based on new Modbus register values."""
        for ld in self.led_dashboards:
            ld[2].update_view(
                registers[ld[1]['register']],
                ld[1]['bits'],
            )

