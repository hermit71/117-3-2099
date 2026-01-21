"""Entry point for the GUI application.

Точка входа для графического приложения.
"""

import sys
import logging

from PyQt6.QtWidgets import QApplication

from src.ui.main_window import MainWindow
from src.utils.config import Config

if __name__ == '__main__':
    logging.basicConfig(level=logging.INFO)
    app = QApplication(sys.argv)
    app.setStyle('Fusion')
    # app.setStyle('Windows11')
    # app.setStyleSheet(STYLE_SHEET)
    config = Config('config/config.yaml')
    window = MainWindow(config)
    window.on_btn_hand_click()
    window.show()
    #window.setGeometry(50, 50, 1920, 1080)
    window.showMaximized()
    sys.exit(app.exec())


