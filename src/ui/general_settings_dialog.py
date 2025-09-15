"""Диалог общих настроек системы."""

from PyQt6.QtWidgets import QDialog

from src.ui.general_settings_dialog_ui import Ui_GeneralSettingsDialog


class GeneralSettingsDialog(QDialog, Ui_GeneralSettingsDialog):
    """Диалог с категориями общих настроек."""

    def __init__(self, parent=None):
        """Инициализирует диалог и настраивает элементы управления."""
        super().__init__(parent)
        self.setupUi(self)

        self.buttonBox.accepted.connect(self.accept)
        self.buttonBox.rejected.connect(self.reject)

        self.categoryList.currentRowChanged.connect(self.pagesStack.setCurrentIndex)
        self.splitter.setStretchFactor(0, 2)
        self.splitter.setStretchFactor(1, 6)
        total_width = self.size().width()
        self.splitter.setSizes([2 * total_width // 8, 6 * total_width // 8])
