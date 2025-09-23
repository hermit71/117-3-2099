"""Диалог настройки параметров ручного ПИД-регулятора."""

from PyQt6.QtCore import Qt, QSize
from PyQt6.QtWidgets import (
    QDialogButtonBox,
    QFormLayout,
    QGroupBox,
    QLabel,
    QLineEdit,
    QVBoxLayout,
)


class HandRegulatorSettingsDialogView:
    """Создаёт интерфейс диалога ручного регулятора программно."""

    def setup_ui(self, dialog):
        """Настроить диалог и вернуть доступ к ключевым элементам."""

        dialog.setObjectName("dlgHandRegulatorSettings")
        dialog.resize(400, 300)

        self.main_layout = QVBoxLayout(dialog)
        self.main_layout.setObjectName("main_layout")

        self.group_box = QGroupBox(parent=dialog)
        self.group_box.setObjectName("group_box")
        self.group_box.setTitle("Настройки ПИД-регулятора")
        self.main_layout.addWidget(self.group_box)

        self.form_layout = QFormLayout(self.group_box)
        self.form_layout.setObjectName("form_layout")

        self.label_kp = QLabel(parent=self.group_box)
        self.label_kp.setObjectName("label_kp")
        self.label_kp.setText("Kp")
        self.input_kp = QLineEdit(parent=self.group_box)
        self.input_kp.setObjectName("input_kp")
        self.input_kp.setMinimumSize(QSize(0, 28))
        self.form_layout.addRow(self.label_kp, self.input_kp)

        self.label_ki = QLabel(parent=self.group_box)
        self.label_ki.setObjectName("label_ki")
        self.label_ki.setText("Ki")
        self.input_ki = QLineEdit(parent=self.group_box)
        self.input_ki.setObjectName("input_ki")
        self.input_ki.setMinimumSize(QSize(0, 28))
        self.form_layout.addRow(self.label_ki, self.input_ki)

        self.label_kd = QLabel(parent=self.group_box)
        self.label_kd.setObjectName("label_kd")
        self.label_kd.setText("Kd")
        self.input_kd = QLineEdit(parent=self.group_box)
        self.input_kd.setObjectName("input_kd")
        self.input_kd.setMinimumSize(QSize(0, 28))
        self.form_layout.addRow(self.label_kd, self.input_kd)

        self.button_box = QDialogButtonBox(parent=dialog)
        self.button_box.setObjectName("button_box")
        self.button_box.setOrientation(Qt.Orientation.Horizontal)
        self.button_box.setStandardButtons(
            QDialogButtonBox.StandardButton.Ok
            | QDialogButtonBox.StandardButton.Cancel
        )
        self.main_layout.addWidget(self.button_box)

        dialog.setWindowTitle("Настройки ПИД-регулятора момента")

        self.button_box.accepted.connect(dialog.accept)
        self.button_box.rejected.connect(dialog.reject)
