"""Построение интерфейса диалога «О программе» без использования Qt Designer."""

from PyQt6.QtCore import Qt
from PyQt6.QtWidgets import QDialogButtonBox, QLabel, QVBoxLayout


class AboutDialogView:
    """Создаёт элементы управления диалога «О программе» программно."""

    def setup_ui(self, dialog):
        """Настроить диалог и вернуть созданные элементы."""

        dialog.setObjectName("AboutDialog")
        dialog.resize(404, 187)

        self.vertical_layout = QVBoxLayout(dialog)
        self.vertical_layout.setObjectName("vertical_layout")

        self.label = QLabel(parent=dialog)
        self.label.setWordWrap(True)
        self.label.setObjectName("label")
        self.vertical_layout.addWidget(self.label)

        self.button_box = QDialogButtonBox(parent=dialog)
        self.button_box.setOrientation(Qt.Orientation.Horizontal)
        self.button_box.setStandardButtons(
            QDialogButtonBox.StandardButton.Ok
        )
        self.button_box.setObjectName("button_box")
        self.vertical_layout.addWidget(self.button_box)

        dialog.setWindowTitle("О программе")
        self.label.setText(
            "Шаблон интерфейса стенда крутильных статических испытаний. "
            "PyQt6 + pyqtgraph + Modbus TCP."
        )

        self.button_box.accepted.connect(dialog.accept)
