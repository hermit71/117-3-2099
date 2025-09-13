"""Top dashboard panel displaying realtime values."""

from PyQt6.QtWidgets import QFrame, QHBoxLayout, QSpacerItem, QSizePolicy
from src.ui.widgets.dashboard_value_widget import ValueWidget


class DashboardPanel(QFrame):
    """Panel with value widgets for tension, velocity and angle."""

    def __init__(self, parent=None, model=None):
        super().__init__(parent)
        self.model = None
        self.value_tension = ValueWidget(self, title='Крутящий момент, Нм')
        self.value_velocity = ValueWidget(self, title='Скорость изменения, Нм/с')
        self.value_angle = ValueWidget(self, title='Угол поворота, \u00B0')
        self.hbox = QHBoxLayout()
        self.hbox.addWidget(self.value_tension)
        self.hbox.addWidget(self.value_velocity)
        self.hbox.addWidget(self.value_angle)
        spacer = QSpacerItem(
            20, 40, QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Minimum
        )
        self.hbox.addItem(spacer)
        self.setLayout(self.hbox)
        self._setup_ui()

    def _setup_ui(self):
        """Reserved for future styling options."""
        pass

    def config(self, model):
        """Attach the application model and connect updates."""
        if model:
            self.model = model
            self.value_tension.data_source = self.model.realtime_data.tension_data_c
            self.value_velocity.data_source = self.model.realtime_data.velocity_data
            self.value_angle.data_source = self.model.realtime_data.angle_data_c
            self.model.graphs_updated.connect(self.value_tension.update)
            self.model.graphs_updated.connect(self.value_velocity.update)
            self.model.graphs_updated.connect(self.value_angle.update)

