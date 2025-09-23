"""Диалог настройки параметров ручного ПИД-регулятора."""

from PyQt6.QtWidgets import QDialog

from src.ui.designer_loader import load_ui


class HandRegulatorSettingsDialog(QDialog):
    """Настройки коэффициентов ПИД-регулятора."""

    def __init__(self, parent=None) -> None:
        super().__init__(parent)
        load_ui(self, "hand_regulator_settings_dialog.ui")

