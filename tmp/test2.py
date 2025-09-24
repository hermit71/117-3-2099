#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
PyQt6: QTableWidget — примеры применения и оформления

Содержимое:
  • Вкладка «Базово»: заполнение, выравнивание, resize-режимы, сортировка
  • Вкладка «Редактирование и сигналы»: триггеры редактирования, обработка cellChanged/ itemSelectionChanged
  • Вкладка «Поиск/фильтр»: простая фильтрация по подстроке
  • Вкладка «Контекстное меню»: Добавить/Удалить строки, Копировать выделение
  • Вкладка «Импорт/Экспорт CSV»: сохранение и загрузка из файла
  • Оформление через QSS: кастомные цвета заголовков, выделения, полос прокрутки (минимально)

Советы:
  • Для очень больших таблиц используйте QTableView + QAbstractTableModel.
  • QTableWidget — item-based API, удобно для небольших таблиц и быстрых прототипов.
"""
from __future__ import annotations

import csv
import sys
from typing import Iterable, List

from PyQt6.QtCore import Qt, QPoint
from PyQt6.QtGui import QAction, QCursor
from PyQt6.QtWidgets import (
    QApplication,
    QWidget,
    QVBoxLayout,
    QHBoxLayout,
    QTableWidget,
    QTableWidgetItem,
    QHeaderView,
    QPushButton,
    QLabel,
    QLineEdit,
    QFileDialog,
    QMessageBox,
    QTabWidget,
    QAbstractItemView,
    QStyledItemDelegate,
    QSpinBox,
    QMenu,
)


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
}

/* Заголовки колонок/строк */
QHeaderView::section {
    background: #F2F5F8;
    color: #334155;
    padding: 6px 8px;
    border: 1px solid #E5E7EB;
    font-weight: 600;
}
QHeaderView::section:hover {
    background: #E8EEF5;
}
QHeaderView::section:checked {
    background: #DDEAF7;
}

/* Ячейки */
QTableWidget::item {
    padding: 4px;
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


# ==========================
# Делегаты (кастомные редакторы/валидация)
# ==========================
class IntSpinDelegate(QStyledItemDelegate):
    """Делегат с редактором QSpinBox для целочисленных значений.
    Пример: ограничиваем значения от 0 до 1000.
    """

    def __init__(self, minimum: int = 0, maximum: int = 1000, parent=None) -> None:
        super().__init__(parent)
        self._min = minimum
        self._max = maximum

    def createEditor(self, parent, option, index):
        spin = QSpinBox(parent)
        spin.setRange(self._min, self._max)
        spin.setFrame(False)
        return spin

    def setEditorData(self, editor: QSpinBox, index):
        try:
            value = int(index.model().data(index, Qt.ItemDataRole.EditRole))
        except (TypeError, ValueError):
            value = 0
        editor.setValue(value)

    def setModelData(self, editor: QSpinBox, model, index):
        model.setData(index, editor.value())


# ==========================
# Вспомогательные функции
# ==========================

def make_table(headers: List[str], rows: Iterable[Iterable[object]]) -> QTableWidget:
    table = QTableWidget()
    table.setColumnCount(len(headers))
    table.setHorizontalHeaderLabels(headers)

    # Базовые настройки UX
    table.setAlternatingRowColors(True)
    table.setSortingEnabled(True)
    table.setWordWrap(False)

    header = table.horizontalHeader()
    header.setStretchLastSection(True)
    header.setSectionResizeMode(QHeaderView.ResizeMode.Interactive)

    # Выделение строк целиком и редактирование по двойному клику
    table.setSelectionBehavior(QAbstractItemView.SelectionBehavior.SelectRows)
    table.setSelectionMode(QAbstractItemView.SelectionMode.ExtendedSelection)
    table.setEditTriggers(
        QAbstractItemView.EditTrigger.DoubleClicked
        | QAbstractItemView.EditTrigger.EditKeyPressed
        | QAbstractItemView.EditTrigger.AnyKeyPressed
    )

    # Заполнение
    rows = list(rows)
    table.setRowCount(len(rows))
    for r, row in enumerate(rows):
        for c, value in enumerate(row):
            item = QTableWidgetItem(str(value))
            # Пример выравнивания: числа — по правому краю
            if isinstance(value, (int, float)):
                item.setTextAlignment(Qt.AlignmentFlag.AlignRight | Qt.AlignmentFlag.AlignVCenter)
            table.setItem(r, c, item)

    return table


def copy_selection_to_clipboard(table: QTableWidget) -> None:
    selection = table.selectedRanges()
    if not selection:
        return
    rng = selection[0]
    parts: List[str] = []
    for r in range(rng.topRow(), rng.bottomRow() + 1):
        row_values: List[str] = []
        for c in range(rng.leftColumn(), rng.rightColumn() + 1):
            item = table.item(r, c)
            row_values.append(item.text() if item else "")
        parts.append("\t".join(row_values))
    QApplication.clipboard().setText("\n".join(parts))


# ==========================
# Вкладки-примеры
# ==========================
class BasicTab(QWidget):
    def __init__(self):
        super().__init__()
        layout = QVBoxLayout(self)

        hdrs = ["ID", "Имя", "Город", "Баллы"]
        data = [
            [1, "Анна", "Москва", 92],
            [2, "Борис", "Санкт-Петербург", 75],
            [3, "Вика", "Казань", 88],
            [4, "Гриша", "Екатеринбург", 61],
            [5, "Дима", "Новосибирск", 97],
        ]
        self.table = make_table(hdrs, data)

        # Показываем разные режимы resize для наглядности
        controls = QHBoxLayout()
        btn_stretch = QPushButton("Растянуть колонки")
        btn_fit = QPushButton("Подогнать по содержимому")
        btn_default = QPushButton("Интерактивный размер")
        controls.addWidget(btn_stretch)
        controls.addWidget(btn_fit)
        controls.addWidget(btn_default)

        btn_stretch.clicked.connect(
            lambda: self.table.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeMode.Stretch)
        )
        btn_fit.clicked.connect(self.resize_to_contents)
        btn_default.clicked.connect(
            lambda: self.table.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeMode.Interactive)
        )

        layout.addLayout(controls)
        layout.addWidget(self.table)

    def resize_to_contents(self):
        header = self.table.horizontalHeader()
        header.setSectionResizeMode(QHeaderView.ResizeMode.ResizeToContents)
        # Немного увеличить последнюю колонку, чтобы не было прижатия
        header.setStretchLastSection(True)


class EditSignalsTab(QWidget):
    def __init__(self):
        super().__init__()
        v = QVBoxLayout(self)
        hdrs = ["Наименование", "Количество", "Цена"]
        data = [["Тетрадь", 5, 19], ["Ручка", 12, 29], ["Папка", 2, 99]]
        self.table = make_table(hdrs, data)

        # Делегат для числовых колонок (кол-во и цена)
        self.table.setItemDelegateForColumn(1, IntSpinDelegate(0, 1000, self))
        self.table.setItemDelegateForColumn(2, IntSpinDelegate(0, 1_000_000, self))

        # Метки для отображения событий
        self.lbl_info = QLabel("Изменений нет.")

        # Сигналы
        self.table.itemChanged.connect(self.on_item_changed)
        self.table.itemSelectionChanged.connect(self.on_selection_changed)

        v.addWidget(self.table)
        v.addWidget(self.lbl_info)

    def on_item_changed(self, item: QTableWidgetItem):
        self.lbl_info.setText(
            f"Изменена ячейка (r={item.row()+1}, c={item.column()+1}) → '{item.text()}'"
        )

    def on_selection_changed(self):
        ranges = self.table.selectedRanges()
        if ranges:
            rng = ranges[0]
            self.lbl_info.setText(
                f"Выделено: {rng.rowCount()}×{rng.columnCount()} (стр. {rng.topRow()+1}–{rng.bottomRow()+1})"
            )
        else:
            self.lbl_info.setText("Выделение снято")


class FilterTab(QWidget):
    def __init__(self):
        super().__init__()
        v = QVBoxLayout(self)

        hdrs = ["ID", "ФИО", "Отдел", "Статус"]
        data = [
            [101, "Иванов И.И.", "Продажи", "Активен"],
            [102, "Петров П.П.", "Маркетинг", "В отпуске"],
            [103, "Сидорова А.А.", "Разработка", "Активен"],
            [104, "Орлова Н.Н.", "Бухгалтерия", "Удалёнка"],
            [105, "Ким С.С.", "Разработка", "Больничный"],
        ]
        self.table = make_table(hdrs, data)
        self.ed_filter = QLineEdit(placeholderText="Фильтр по всем колонкам…")
        self.ed_filter.textChanged.connect(self.apply_filter)

        v.addWidget(self.ed_filter)
        v.addWidget(self.table)

    def apply_filter(self, text: str):
        text = text.strip().lower()
        for r in range(self.table.rowCount()):
            visible = False
            for c in range(self.table.columnCount()):
                item = self.table.item(r, c)
                if item and text in item.text().lower():
                    visible = True
                    break
            self.table.setRowHidden(r, not visible)


class ContextMenuTab(QWidget):
    def __init__(self):
        super().__init__()
        v = QVBoxLayout(self)
        hdrs = ["№", "Товар", "Цена"]
        data = [[1, "Карандаш", 15], [2, "Ластик", 20], [3, "Линейка", 35]]
        self.table = make_table(hdrs, data)

        # Контекстное меню по правому клику
        self.table.setContextMenuPolicy(Qt.ContextMenuPolicy.CustomContextMenu)
        self.table.customContextMenuRequested.connect(self.open_menu)

        # Подписи с подсказками
        hint = QLabel(
            "Правый клик по таблице → контекстное меню (Добавить, Удалить, Копировать).\n"
            "Поддерживается множественное выделение строк."
        )

        v.addWidget(self.table)
        v.addWidget(hint)

    def open_menu(self, pos: QPoint):
        menu = QMenu(self)
        act_add = QAction("Добавить строку", self)
        act_del = QAction("Удалить выделенные", self)
        act_copy = QAction("Копировать (TSV)", self)

        act_add.triggered.connect(self.add_row)
        act_del.triggered.connect(self.remove_selected_rows)
        act_copy.triggered.connect(lambda: copy_selection_to_clipboard(self.table))

        menu.addAction(act_add)
        menu.addAction(act_del)
        menu.addSeparator()
        menu.addAction(act_copy)

        menu.exec(QCursor.pos())

    def add_row(self):
        row = self.table.rowCount()
        self.table.insertRow(row)
        # Проставим № автоматически
        self.table.setItem(row, 0, QTableWidgetItem(str(row + 1)))

    def remove_selected_rows(self):
        rows = sorted({i.row() for i in self.table.selectedItems()}, reverse=True)
        for r in rows:
            self.table.removeRow(r)


class CsvTab(QWidget):
    def __init__(self):
        super().__init__()
        v = QVBoxLayout(self)
        hdrs = ["Код", "Название", "Категория", "Цена"]
        data = [
            ["A-100", "Степлер", "Офис", 250],
            ["A-101", "Скотч", "Офис", 60],
            ["B-200", "Кружка", "Кухня", 320],
        ]
        self.table = make_table(hdrs, data)

        btns = QHBoxLayout()
        btn_load = QPushButton("Загрузить CSV…")
        btn_save = QPushButton("Сохранить CSV…")
        btns.addWidget(btn_load)
        btns.addWidget(btn_save)

        btn_load.clicked.connect(self.load_csv)
        btn_save.clicked.connect(self.save_csv)

        v.addLayout(btns)
        v.addWidget(self.table)

    def save_csv(self):
        path, _ = QFileDialog.getSaveFileName(self, "Сохранить как", "table.csv", "CSV (*.csv)")
        if not path:
            return
        with open(path, "w", newline="", encoding="utf-8") as f:
            writer = csv.writer(f)
            headers = [self.table.horizontalHeaderItem(c).text() for c in range(self.table.columnCount())]
            writer.writerow(headers)
            for r in range(self.table.rowCount()):
                row: List[str] = []
                for c in range(self.table.columnCount()):
                    item = self.table.item(r, c)
                    row.append(item.text() if item else "")
                writer.writerow(row)

    def load_csv(self):
        path, _ = QFileDialog.getOpenFileName(self, "Открыть CSV", "", "CSV (*.csv)")
        if not path:
            return
        try:
            with open(path, "r", newline="", encoding="utf-8") as f:
                reader = csv.reader(f)
                rows = list(reader)
        except Exception as e:
            QMessageBox.critical(self, "Ошибка", f"Не удалось прочитать файл: {e}")
            return
        if not rows:
            return
        headers = rows[0]
        data = rows[1:]
        self.table.clear()
        self.table.setRowCount(0)
        self.table.setColumnCount(len(headers))
        self.table.setHorizontalHeaderLabels(headers)
        self.table.setRowCount(len(data))
        for r, row in enumerate(data):
            for c, value in enumerate(row):
                self.table.setItem(r, c, QTableWidgetItem(value))


class TableWidgetExamples(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("QTableWidget — примеры (PyQt6)")
        self.resize(880, 560)

        v = QVBoxLayout(self)
        tabs = QTabWidget()
        tabs.addTab(BasicTab(), "Базово")
        tabs.addTab(EditSignalsTab(), "Редактирование и сигналы")
        tabs.addTab(FilterTab(), "Поиск/фильтр")
        tabs.addTab(ContextMenuTab(), "Контекстное меню")
        tabs.addTab(CsvTab(), "Импорт/Экспорт CSV")
        v.addWidget(tabs)


def main():
    app = QApplication(sys.argv)
    app.setStyleSheet(STYLE_SHEET)
    w = TableWidgetExamples()
    w.show()
    sys.exit(app.exec())


if __name__ == "__main__":
    main()
