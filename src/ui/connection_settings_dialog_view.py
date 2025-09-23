"""Интерфейс диалога настройки параметров соединения Modbus."""

from PyQt6.QtCore import Qt
from PyQt6.QtWidgets import (
    QDialogButtonBox,
    QFormLayout,
    QLabel,
    QLineEdit,
)


class ConnectionSettingsDialogView:
    """Создаёт элементы диалога настроек соединения программно."""

    def setup_ui(self, dialog):
        """Создать элементы управления диалога и подключить сигналы."""

        dialog.setObjectName("ConnectionSettingsDialog")
        dialog.resize(400, 200)

        self.form_layout = QFormLayout(dialog)
        self.form_layout.setObjectName("form_layout")

        self.label_host = QLabel(parent=dialog)
        self.label_host.setObjectName("label_host")
        self.label_host.setText("IP-адрес ПЛК:")
        self.form_layout.setWidget(0, QFormLayout.ItemRole.LabelRole, self.label_host)

        self.ed_host = QLineEdit(parent=dialog)
        self.ed_host.setObjectName("ed_host")
        self.ed_host.setPlaceholderText("например, 192.168.0.1")
        self.form_layout.setWidget(0, QFormLayout.ItemRole.FieldRole, self.ed_host)

        self.label_port = QLabel(parent=dialog)
        self.label_port.setObjectName("label_port")
        self.label_port.setText("Порт:")
        self.form_layout.setWidget(1, QFormLayout.ItemRole.LabelRole, self.label_port)

        self.ed_port = QLineEdit(parent=dialog)
        self.ed_port.setObjectName("ed_port")
        self.ed_port.setPlaceholderText("например, 502")
        self.form_layout.setWidget(1, QFormLayout.ItemRole.FieldRole, self.ed_port)

        self.label_timeout = QLabel(parent=dialog)
        self.label_timeout.setObjectName("label_timeout")
        self.label_timeout.setText("Таймаут (с):")
        self.form_layout.setWidget(2, QFormLayout.ItemRole.LabelRole, self.label_timeout)

        self.ed_timeout = QLineEdit(parent=dialog)
        self.ed_timeout.setObjectName("ed_timeout")
        self.form_layout.setWidget(2, QFormLayout.ItemRole.FieldRole, self.ed_timeout)

        self.label_poll = QLabel(parent=dialog)
        self.label_poll.setObjectName("label_poll")
        self.label_poll.setText("Период опроса (мс):")
        self.form_layout.setWidget(3, QFormLayout.ItemRole.LabelRole, self.label_poll)

        self.ed_poll = QLineEdit(parent=dialog)
        self.ed_poll.setObjectName("ed_poll")
        self.form_layout.setWidget(3, QFormLayout.ItemRole.FieldRole, self.ed_poll)

        self.button_box = QDialogButtonBox(parent=dialog)
        self.button_box.setOrientation(Qt.Orientation.Horizontal)
        self.button_box.setStandardButtons(
            QDialogButtonBox.StandardButton.Ok
            | QDialogButtonBox.StandardButton.Cancel
        )
        self.button_box.setObjectName("button_box")
        self.form_layout.setWidget(4, QFormLayout.ItemRole.SpanningRole, self.button_box)

        dialog.setWindowTitle("Параметры соединения")

        self.button_box.accepted.connect(dialog.accept)
        self.button_box.rejected.connect(dialog.reject)
