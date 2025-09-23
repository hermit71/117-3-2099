"""Диалог «О программе», загружаемый из Qt Designer."""

from PyQt6.QtWidgets import QDialog

from src.ui.designer_loader import load_ui


class AboutDialog(QDialog):
    """Простое информационное окно."""

    def __init__(self, parent=None) -> None:
        super().__init__(parent)
        load_ui(self, "about_dialog.ui")

