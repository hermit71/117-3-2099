"""Программный интерфейс диалога настройки графиков."""

from PyQt6.QtCore import Qt
from PyQt6.QtWidgets import QDialogButtonBox, QVBoxLayout


class GraphSettingsDialogView:
    """Готовит контейнеры для настроек графиков."""

    def setup_ui(self, dialog):
        """Создать основной макет диалога."""

        dialog.setObjectName("GraphSettingsDialog")
        dialog.resize(400, 300)

        self.main_layout = QVBoxLayout(dialog)
        self.main_layout.setObjectName("main_layout")

        self.graphs_layout = QVBoxLayout()
        self.graphs_layout.setObjectName("graphs_layout")
        self.main_layout.addLayout(self.graphs_layout)

        self.button_box = QDialogButtonBox(parent=dialog)
        self.button_box.setObjectName("button_box")
        self.button_box.setOrientation(Qt.Orientation.Horizontal)
        self.button_box.setStandardButtons(
            QDialogButtonBox.StandardButton.Ok
            | QDialogButtonBox.StandardButton.Cancel
        )
        self.main_layout.addWidget(self.button_box)

        dialog.setWindowTitle("Настройки графиков")

        self.button_box.accepted.connect(dialog.accept)
        self.button_box.rejected.connect(dialog.reject)
