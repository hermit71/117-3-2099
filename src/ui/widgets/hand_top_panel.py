"""Top dashboard panel displaying realtime values."""
from PyQt6.QtCore import QObject, QTimer
from PyQt6.QtWidgets import QFrame, QHBoxLayout, QSpacerItem, QSizePolicy, QPushButton
from src.ui.widgets.dashboard_value_widget import ValueDisplay

class DashboardPanel(QFrame):
    """Panel with value widgets for tension, velocity and angle."""

    def __init__(self, parent=None, model=None):
        super().__init__(parent)
        self.model = None
        self.update_time = 100 # ms
        self.value_torque       = ValueDisplay(self)
        self.value_velocity     = ValueDisplay(self)
        self.value_angle        = ValueDisplay(self)
        self.value_time_elapsed = ValueDisplay(self)
        self._setup_ui()
        self.timer = QTimer()
        self.timer.timeout.connect(self.on_timer)
        self.timer.start(self.update_time)

    def _setup_ui(self):
        self.hbox = QHBoxLayout()
        self.hbox.setSpacing(18)
        self.hbox.setContentsMargins(0, 0, 0, 0)
        self.hbox.addWidget(self.value_torque)
        self.hbox.addWidget(self.value_velocity)
        self.hbox.addWidget(self.value_angle)
        self.hbox.addWidget(self.value_time_elapsed)
        spacer = QSpacerItem(
            20, 40, QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Minimum
        )
        self.hbox.addItem(spacer)
        self.setLayout(self.hbox)
        self.value_torque.set_title("Крутящий момент, Нм")
        self.value_velocity.set_title("Скорость изменения, Нм/с")
        self.value_angle.set_title("Угол поворота, \u00B0")
        self.value_time_elapsed.set_title("Время, с")


    def on_timer(self):
        self.value_torque.update()
        self.value_velocity.update()
        self.value_angle.update()
        self.value_time_elapsed.update()


    def config(self, model):
        """Attach the application model and connect updates."""
        pass
        if model:
            self.model = model
            self.value_torque.set_data_source(self.model.realtime_data.get_torque)
            self.value_velocity.set_data_source(self.model.realtime_data.get_velocity)
            self.value_angle.set_data_source(self.model.realtime_data.get_angle)


