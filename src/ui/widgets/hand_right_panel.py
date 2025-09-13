"""LED dashboard panel for manual control screen."""

import logging

from PyQt6.QtWidgets import QFrame, QSpacerItem, QSizePolicy, QVBoxLayout
from PyQt6.QtCore import pyqtSlot as Slot

from src.ui.widgets.led_panel import LedPanel

logger = logging.getLogger(__name__)

class LedDashboardPanel(QFrame):
    """Panel containing LED dashboards for manual mode."""

    def __init__(self, parent=None):
        super().__init__(parent)
        self.model = None
        self.led_dashboards = None
        self.vbox = QVBoxLayout()

    def config(self, model=None, led_dashboards=None):
        """Configure panel with model and dashboard definitions."""
        self.model = model
        self.led_dashboards = led_dashboards
        self.setup_ui()
        self.model.data_updated.connect(self.data_update)

    def setup_ui(self):
        """Create LED panels and layout."""
        if self.led_dashboards is None:
            logger.info("No led_dashboards defined")
            return
        for i, ld in enumerate(self.led_dashboards):
            led_p = LedPanel(
                led_number=ld[1]["num"],
                title=ld[1]["title"],
                labels=ld[1]["labels"],
            )
            # Добавляем в список led панелей созданный экземпляр панели
            self.led_dashboards[i].append(led_p)
            self.vbox.addWidget(led_p)
        spacer_item = QSpacerItem(
            20, 40, QSizePolicy.Policy.Minimum, QSizePolicy.Policy.Expanding
        )
        self.vbox.addItem(spacer_item)
        self.setLayout(self.vbox)

    @Slot(list)
    def data_update(self, registers):
        """Update LED panels based on Modbus registers."""
        for i, ld in enumerate(self.led_dashboards):
            ld[2].update_view(
                registers[ld[1]["register"]],  # Обновляем состояние led панели
                ld[1]["bits"],  # и нужными битами этого регистра
            )