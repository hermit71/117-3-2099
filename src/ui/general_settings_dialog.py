"""Диалог общих настроек системы."""

from typing import Optional

from PyQt6.QtWidgets import QDialog

from src.ui.general_settings_dialog_ui import Ui_GeneralSettingsDialog
from src.utils.config import Config


class GeneralSettingsDialog(QDialog, Ui_GeneralSettingsDialog):
    """Диалог с категориями общих настроек."""

    def __init__(self, parent=None, config: Optional[Config] = None):
        """Инициализирует диалог, загружая данные о стенде из настроек."""
        super().__init__(parent)
        self.config = config
        self.setupUi(self)

        self.buttonBox.accepted.connect(self.accept)
        self.buttonBox.rejected.connect(self.reject)

        self.categoryList.currentRowChanged.connect(self.pagesStack.setCurrentIndex)
        self.splitter.setStretchFactor(0, 2)
        self.splitter.setStretchFactor(1, 6)
        total_width = self.size().width()
        self.splitter.setSizes([2 * total_width // 8, 6 * total_width // 8])

        self._stand_fields = {
            "lab_address": self.lineLabAddress,
            "brand_and_model": self.lineStandModel,
            "serial_number": self.lineSerialNumber,
            "certification_date": self.lineCertificationDate,
        }

        self._load_stand_info()

    def _load_stand_info(self) -> None:
        """Заполнить поля данными из конфигурации."""

        if not self.config:
            for line_edit in self._stand_fields.values():
                line_edit.clear()
            return

        for key, line_edit in self._stand_fields.items():
            line_edit.setText(self.config.get("stand", key, ""))

    def _save_stand_info(self) -> None:
        """Сохранить введённые пользователем данные в конфигурации."""

        if not self.config:
            return

        stand_section = self.config.cfg.setdefault("stand", {})
        for key, line_edit in self._stand_fields.items():
            stand_section[key] = line_edit.text().strip()

    def accept(self) -> None:
        """Сохранить данные и закрыть диалог."""

        self._save_stand_info()
        if self.config:
            self.config.save()
        super().accept()
