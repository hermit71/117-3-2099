"""Программное построение диалога общих настроек системы."""

from PyQt6.QtCore import Qt
from PyQt6.QtWidgets import (
    QDialogButtonBox,
    QGridLayout,
    QListWidget,
    QListWidgetItem,
    QLineEdit,
    QSizePolicy,
    QSpacerItem,
    QSplitter,
    QStackedWidget,
    QVBoxLayout,
    QWidget,
    QLabel,
)


class GeneralSettingsDialogView:
    """Создаёт структуры диалога общих настроек в коде."""

    def setup_ui(self, dialog):
        """Построить интерфейс диалога и подключить кнопки."""

        dialog.setObjectName("GeneralSettingsDialog")
        dialog.resize(600, 400)

        self.main_layout = QVBoxLayout(dialog)
        self.main_layout.setObjectName("main_layout")

        self.splitter = QSplitter(Qt.Orientation.Horizontal, parent=dialog)
        self.splitter.setObjectName("splitter")
        self.main_layout.addWidget(self.splitter)

        self.category_list = QListWidget(parent=self.splitter)
        self.category_list.setObjectName("category_list")
        for title in (
            "Система",
            "Общие данные стенда",
            "Соединение",
            "Отчеты",
            "Архив",
        ):
            QListWidgetItem(title, self.category_list)

        self.pages_stack = QStackedWidget(parent=self.splitter)
        self.pages_stack.setObjectName("pages_stack")

        self.page_system = QWidget()
        self.page_system.setObjectName("page_system")
        self.pages_stack.addWidget(self.page_system)

        self.page_general = QWidget()
        self.page_general.setObjectName("page_general")
        self.general_layout = QGridLayout(self.page_general)
        self.general_layout.setObjectName("general_layout")

        self.label_lab_address = QLabel(parent=self.page_general)
        self.label_lab_address.setObjectName("label_lab_address")
        self.label_lab_address.setText("Адрес лаборатории:")
        self.general_layout.addWidget(self.label_lab_address, 0, 0, 1, 1)

        self.line_lab_address = QLineEdit(parent=self.page_general)
        self.line_lab_address.setObjectName("line_lab_address")
        self.general_layout.addWidget(self.line_lab_address, 0, 1, 1, 1)

        self.label_stand_model = QLabel(parent=self.page_general)
        self.label_stand_model.setObjectName("label_stand_model")
        self.label_stand_model.setText("Марка и модель стенда:")
        self.general_layout.addWidget(self.label_stand_model, 1, 0, 1, 1)

        self.line_stand_model = QLineEdit(parent=self.page_general)
        self.line_stand_model.setObjectName("line_stand_model")
        self.general_layout.addWidget(self.line_stand_model, 1, 1, 1, 1)

        self.label_serial_number = QLabel(parent=self.page_general)
        self.label_serial_number.setObjectName("label_serial_number")
        self.label_serial_number.setText("Серийный номер стенда:")
        self.general_layout.addWidget(self.label_serial_number, 2, 0, 1, 1)

        self.line_serial_number = QLineEdit(parent=self.page_general)
        self.line_serial_number.setObjectName("line_serial_number")
        self.general_layout.addWidget(self.line_serial_number, 2, 1, 1, 1)

        self.label_certification_date = QLabel(parent=self.page_general)
        self.label_certification_date.setObjectName("label_certification_date")
        self.label_certification_date.setText("Дата аттестации стенда:")
        self.general_layout.addWidget(self.label_certification_date, 3, 0, 1, 1)

        self.line_certification_date = QLineEdit(parent=self.page_general)
        self.line_certification_date.setObjectName("line_certification_date")
        self.general_layout.addWidget(self.line_certification_date, 3, 1, 1, 1)

        spacer = QSpacerItem(
            20,
            40,
            QSizePolicy.Policy.Minimum,
            QSizePolicy.Policy.Expanding,
        )
        self.general_layout.addItem(spacer, 4, 0, 1, 1)

        self.pages_stack.addWidget(self.page_general)

        self.page_connection = QWidget()
        self.page_connection.setObjectName("page_connection")
        self.pages_stack.addWidget(self.page_connection)

        self.page_reports = QWidget()
        self.page_reports.setObjectName("page_reports")
        self.pages_stack.addWidget(self.page_reports)

        self.page_archive = QWidget()
        self.page_archive.setObjectName("page_archive")
        self.pages_stack.addWidget(self.page_archive)

        self.button_box = QDialogButtonBox(parent=dialog)
        self.button_box.setObjectName("button_box")
        self.button_box.setOrientation(Qt.Orientation.Horizontal)
        self.button_box.setStandardButtons(
            QDialogButtonBox.StandardButton.Ok
            | QDialogButtonBox.StandardButton.Cancel
        )
        self.main_layout.addWidget(self.button_box)

        dialog.setWindowTitle("Общие настройки системы")

        self.button_box.accepted.connect(dialog.accept)
        self.button_box.rejected.connect(dialog.reject)
