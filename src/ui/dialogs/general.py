"""Диалог общих настроек системы."""

from __future__ import annotations

from typing import Dict, Optional

from PyQt6.QtWidgets import QDialog, QLineEdit

from src.ui.designer_loader import load_ui
from src.utils.config import Config


class GeneralSettingsDialog(QDialog):
    """Диалог с категориями общих настроек."""

    def __init__(self, parent=None, config: Optional[Config] = None) -> None:
        super().__init__(parent)
        self.config = config
        load_ui(self, "general_settings_dialog.ui")
        self.category_list.currentRowChanged.connect(
            self.pages_stack.setCurrentIndex
        )
        self.splitter.setStretchFactor(0, 2)
        self.splitter.setStretchFactor(1, 6)
        total_width = max(self.size().width(), 1)
        self.splitter.setSizes([2 * total_width // 8, 6 * total_width // 8])

        self._stand_fields: Dict[str, QLineEdit] = {
            "lab_address": self.line_lab_address,
            "brand_and_model": self.line_stand_model,
            "serial_number": self.line_serial_number,
            "certification_date": self.line_certification_date,
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

    def accept(self) -> None:  # noqa: D401
        """Сохранить данные и закрыть диалог."""

        self._save_stand_info()
        if self.config:
            self.config.save()
        super().accept()

