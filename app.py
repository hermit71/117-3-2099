"""Entry point for the GUI application.

Точка входа для графического приложения.
"""

import sys
import logging

from PyQt6.QtWidgets import QApplication

from src.ui.main_window import MainWindow
from src.utils.config import Config


# ==========================
# Оформление (QSS стили)
# ==========================
STYLE_SHEET = """
/* Фон и границы таблицы */
QTableWidget {
    gridline-color: #E0E0E0;
    selection-background-color: #CCE5FF; /* fallback для старых тем */
    selection-color: #0B1F33;
    alternate-background-color: #FAFAFA;
    font-size: 14px;
    font-family: "Inconsolata LGC Nerd Font", "Segoe UI", Arial, sans-serif;
}

/* Заголовки колонок/строк */
QHeaderView::section {
    background: #F2F5F8;
    color: #334155;
    padding: 6px 8px;
    border: 1px solid #E5E7EB;
    font-weight: 600;
    font-size: 14px;
}
QHeaderView::section:hover {
    background: #E8EEF5;
}
QHeaderView::section:checked {
    background: #DDEAF7;
}

/* Ячейки */
QTableWidget::item {
    padding: 0px;
    font-family: "Inconsolata LGC Nerd Font", "Segoe UI", Arial, sans-serif;
}
QTableWidget::item:selected {
    background: #CDEAFE; /* цвет выделения */
    color: #0B1F33;
}
QTableWidget::item:hover {
    background: #F3F8FF;
}

/* Кнопка в углу между заголовками */
QTableCornerButton::section {
    background: #F2F5F8;
    border: 1px solid #E5E7EB;
}

/* Полосы прокрутки — минимум стилей, чтобы не перегружать */
QScrollBar:vertical, QScrollBar:horizontal {
    background: transparent;
}
QScrollBar::handle:vertical, QScrollBar::handle:horizontal {
    background: #CBD5E1;
    border-radius: 4px;
}
"""

if __name__ == '__main__':
    logging.basicConfig(level=logging.INFO)
    app = QApplication(sys.argv)
    app.setStyle('Fusion')
    # app.setStyle('Windows11')
    app.setStyleSheet(STYLE_SHEET)
    config = Config('config/config.yaml')
    window = MainWindow(config)
    # window.setGeometry(50, 50, 1700, 900)
    window.on_btn_hand_click()
    window.show()
    window.showMaximized()
    sys.exit(app.exec())


