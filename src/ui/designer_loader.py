"""Утилиты для загрузки форм Qt Designer во время выполнения."""

from pathlib import Path
from typing import Union

from PyQt6 import uic
from PyQt6.QtWidgets import QWidget

# Импортируем пользовательские виджеты, чтобы ``uic`` смог сопоставить их по
# именам, объявленным в ``.ui`` файлах.  Сами классы не используются напрямую в
# коде модуля, поэтому подавляем предупреждения линтера.
from src.ui.widgets.graph_widget import GraphWidget  # noqa: F401
from src.ui.widgets.hand_right_panel import LedDashboardPanel  # noqa: F401
from src.ui.widgets.hand_top_panel import DashboardPanel  # noqa: F401
from src.utils.spin_box_int_to_float import AppSpinBox  # noqa: F401
from src.ui.widgets.calibration_widget import ServoCalibrationWidget


UI_DIR = Path(__file__).resolve().parent


def load_ui(base: QWidget, ui_filename: Union[str, Path]) -> None:
    """Загрузить интерфейс из ``.ui`` файла в существующий экземпляр.

    Parameters
    ----------
    base:
        Виджет, в который необходимо загрузить форму.
    ui_filename:
        Имя файла формы относительно текущего пакета ``src.ui``.
    """

    ui_path = UI_DIR / ui_filename
    if not ui_path.exists():
        raise FileNotFoundError(f"Не найден файл интерфейса: {ui_path}")
    uic.loadUi(ui_path, base)

