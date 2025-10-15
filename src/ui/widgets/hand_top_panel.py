"""Top dashboard panel displaying realtime values."""
from PyQt6.QtCore import QObject
from PyQt6.QtWidgets import QFrame, QHBoxLayout, QSpacerItem, QSizePolicy
from src.ui.widgets.dashboard_value_widget import ValueWidget, ValueDisplay

class ValueSource(QObject):
    def __init__(self, source):
        super().__init__()
        self.source = source

    def get_value(self):
        return self.source()

class DashboardPanel(QFrame):
    """Panel with value widgets for tension, velocity and angle."""

    def __init__(self, parent=None, model=None):
        super().__init__(parent)
        self.model = None
        #self.value_tension = ValueWidget(self, title='Крутящий момент, Нм')
        #self.value_velocity = ValueWidget(self, title='Скорость изменения, Нм/с')
        #self.value_angle = ValueWidget(self, title='Угол поворота, \u00B0')
        self.value_tension = ValueDisplay(self)
        self.value_velocity = ValueDisplay(self)
        self.value_angle = ValueDisplay(self)
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
        pass
        if model:
            self.model = model
            tension_source = ValueSource(self.model.realtime_data.get_tension)
            self.value_tension._set_data_source(tension_source)
            #self.value_velocity.data_source = "velocity"
            #self.value_angle.data_source = "angle"
            #self.model.graphs_updated.connect(self.value_tension.update)
            #self.model.graphs_updated.connect(self.value_velocity.update)
            #self.model.graphs_updated.connect(self.value_angle.update)

