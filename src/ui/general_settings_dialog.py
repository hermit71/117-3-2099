"""Диалог общих настроек системы."""

from PyQt6.QtWidgets import QDialog

from src.ui.general_settings_dialog_ui import Ui_GeneralSettingsDialog


class GeneralSettingsDialog(QDialog, Ui_GeneralSettingsDialog):
    """Пустой диалог с общими настройками системы."""

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setupUi(self)
        self.buttonBox.accepted.connect(self.accept)
        self.buttonBox.rejected.connect(self.reject)
