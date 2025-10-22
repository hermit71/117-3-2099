# -*- coding: utf-8 -*-
"""
TimeSeriesPlotWidget (PyQt6 + pyqtgraph)
— наследник pyqtgraph.PlotWidget со «скользящим окном» и мышиной прокруткой по X,
при этом метки времени (ось X) остаются фиксированными.

Изменения относительно предыдущей версии:
- Переведено на PyQt6.
- Добавлен перетаскиваемый просмотр: мышкой можно двигать отображаемый срез вдоль X,
  при этом ось X (0 .. x_window_seconds) остаётся неподвижной — двигается только график
  (подгружается другой срез исходного датасета).
- Сохранены методы конфигурации внешнего вида и API обновления.

Зависимости: PyQt6, pyqtgraph, numpy.
"""
from __future__ import annotations
from typing import Dict, Optional, Tuple, Union

import numpy as np

from PyQt6 import QtCore, QtGui, QtWidgets
import pyqtgraph as pg


Number = Union[int, float]
ColorLike = Union[str, Tuple[int, int, int], Tuple[int, int, int, int], pg.QtGui.QColor]


class _PanViewBox(pg.ViewBox):
    """Пользовательский ViewBox: вместо сдвига диапазонов осей меняем «курсор-срез».

    Сигнал panRequested(dx_seconds) сообщает, на сколько секунд пользователь
    перетянул график (dx может быть положительным или отрицательным).
    """

    panRequested = QtCore.pyqtSignal(float)

    def __init__(self, *args, **kwargs) -> None:
        super().__init__(*args, **kwargs)
        self.setMouseEnabled(x=False, y=False)  # штатное панорамирование отключаем
        self._last_mouse_pos: Optional[QtCore.QPointF] = None

    def mouseDragEvent(self, ev: pg.MouseDragEvent) -> None:  # type: ignore[override]
        if ev.button() == pg.QtCore.Qt.MouseButton.LeftButton:
            if ev.isStart():
                self._last_mouse_pos = ev.pos()
                ev.accept()
                return
            if ev.isFinish():
                self._last_mouse_pos = None
                ev.accept()
                return
            if self._last_mouse_pos is None:
                self._last_mouse_pos = ev.pos()

            # Переводим дельту из экранных координат в координаты графика (секунды)
            p1 = self.mapSceneToView(self._last_mouse_pos)
            p2 = self.mapSceneToView(ev.pos())
            dx_seconds = (p1.x() - p2.x())  # знак: тянем влево — смотрим «вперёд» по времени
            self._last_mouse_pos = ev.pos()
            self.panRequested.emit(float(dx_seconds))
            ev.accept()
        else:
            ev.ignore()

    def wheelEvent(self, ev: pg.GraphicsSceneWheelEvent) -> None:  # type: ignore[override]
        # Отключаем масштабирование колёсиком для X, чтобы ось оставалась фиксированной
        ev.ignore()


class TimeSeriesPlotWidget(pg.PlotWidget):
    """Виджет временных рядов со скользящим окном и мышиной прокруткой.

    Ось X фиксирована в пределах [0 .. x_window_seconds] и не двигается; при
    перетаскивании мышью подменяется отображаемый срез данных.

    Параметры
    ---------
    x_window_seconds : float, default 30.0
        Длина окна по оси X (сек).
    points_per_window : int, default 1200
        Количество точек в окне.
    y_range : (float, float), default (-1.0, 1.0)
        Фиксированный диапазон Y.
    background : str, default 'k'
        Цвет фона.
    antialias : bool, default True
        Гладкое рисование линий.
    with_legend : bool, default True
        Показывать легенду.
    """

    dataUpdated = QtCore.pyqtSignal(int, int)  # (start_idx, end_idx)

    def __init__(
        self,
        x_window_seconds: float = 30.0,
        points_per_window: int = 1200,
        y_range: Tuple[Number, Number] = (-1.0, 1.0),
        background: str = "w",
        antialias: bool = True,
        with_legend: bool = True,
        parent: Optional[QtWidgets.QWidget] = None,
    ) -> None:
        # Используем свой ViewBox, чтобы перехватывать жесты панорамирования
        self._vb = _PanViewBox()
        super().__init__(parent=parent, background=background, viewBox=self._vb)

        # Хранение параметров окна
        self._x_window_seconds: float = float(x_window_seconds)
        self._points_per_window: int = int(points_per_window)
        self._dt: float = self._x_window_seconds / max(1, (self._points_per_window - 1))
        self._y_range: Tuple[Number, Number] = y_range

        # Внешний вид
        self.setMenuEnabled(False)
        self.plotItem.setMenuEnabled(False)
        self.plotItem.showGrid(x=True, y=True, alpha=0.3)
        self.set_axis_labels("Время, с", "Амплитуда")
        self.set_y_range(*y_range)
        self.plotItem.enableAutoRange(x=False, y=False)
        self.plotItem.setClipToView(True)
        self.plotItem.setMouseEnabled(x=False, y=False)  # фиксируем оси
        self.plotItem.setXRange(0.0, self._x_window_seconds, padding=0.0)
        self.plotItem.setDefaultPadding(0.0)
        if antialias:
            pg.setConfigOptions(antialias=True)

        # Легенда (лениво)
        self._legend: Optional[pg.LegendItem] = None
        if with_legend:
            self.set_legend(visible=True)

        # Серии (имя -> PlotDataItem)
        self._series: Dict[str, pg.PlotDataItem] = {}

        # Предвычислённый X-массив для окна [0..x_window_seconds]
        self._x_window = np.linspace(0.0, self._x_window_seconds, self._points_per_window)

        # Состояние курсора/среза
        self._last_slice: Tuple[int, int] = (0, self._points_per_window)
        self._cursor_index: int = 0

        # Хранилище данных (опционально; можно продолжать пользоваться update(data, cursor))
        self._data: Optional[np.ndarray] = None

        # Стандартная серия по умолчанию
        self.add_series("Сигнал", color="#0055ee", width=1.0)

        # Подписка на жест панорамирования
        self._vb.panRequested.connect(self._on_pan_seconds)

    # ------------- Публичная конфигурация -------------
    def set_axis_labels(self, x_label: str = "Время, с", y_label: str = "Амплитуда") -> None:
        self.plotItem.setLabel("bottom", x_label)
        self.plotItem.setLabel("left", y_label)

    def set_fonts(self, label_point_size: int = 11, tick_point_size: int = 9, family: str = "Segoe UI") -> None:
        label_font = QtGui.QFont(family, label_point_size)
        tick_font = QtGui.QFont(family, tick_point_size)
        for axis in ("left", "bottom", "right", "top"):
            ax = self.getPlotItem().getAxis(axis)
            if ax is None:
                continue
            ax.setTickFont(tick_font)
        self.getPlotItem().getAxis("left").setStyle(tickTextOffset=10)
        self.getPlotItem().getAxis("bottom").setStyle(tickTextOffset=10)

    def set_grid(self, visible: bool = True, alpha: float = 0.3) -> None:
        self.plotItem.showGrid(x=visible, y=visible, alpha=alpha)

    def set_background(self, color: ColorLike = "k") -> None:
        self.setBackground(color)

    def set_y_range(self, y_min: Number, y_max: Number) -> None:
        self._y_range = (y_min, y_max)
        self.plotItem.setYRange(y_min, y_max, padding=0.0)

    def set_x_window(self, seconds: float, points: Optional[int] = None) -> None:
        self._x_window_seconds = float(seconds)
        if points is not None:
            self._points_per_window = int(points)
        self._dt = self._x_window_seconds / max(1, (self._points_per_window - 1))
        self._x_window = np.linspace(0.0, self._x_window_seconds, self._points_per_window)
        self.plotItem.setXRange(0.0, self._x_window_seconds, padding=0.0)
        # Перерисуем, чтобы x соответствовал новому окну
        for item in self._series.values():
            y = item.yData if item.yData is not None else np.zeros(self._points_per_window)
            y = self._fit_to_window(np.asarray(y))
            item.setData(self._x_window, y, connect='finite')

    def set_legend(self, visible: bool = True, **kwargs) -> None:
        if visible and self._legend is None:
            self._legend = self.plotItem.addLegend(**{"offset": (10, 10), **kwargs})
        elif not visible and self._legend is not None:
            self.plotItem.removeItem(self._legend)
            self._legend = None

    def add_series(self, name: str, color: ColorLike = "#00E5FF", width: float = 2.0) -> pg.PlotDataItem:
        if name in self._series:
            return self._series[name]
        pen = pg.mkPen(color=color, width=width)
        item = self.plot(self._x_window, np.zeros_like(self._x_window), pen=pen, name=name)
        self._series[name] = item
        return item

    def set_series_pen(self, name: str, color: ColorLike = "#00E5FF", width: float = 2.0) -> None:
        if name in self._series:
            self._series[name].setPen(pg.mkPen(color=color, width=width))

    # ------------- Управление данными -------------
    def set_data(self, data: np.ndarray) -> None:
        """Сохранить датасет внутри виджета для панорамирования мышью.

        Поддерживается 1D (N,) и 2D (n_series, N). Если серий данных больше,
        чем уже добавлено в график — недостающие серии будут созданы автоматически.
        """
        if not isinstance(data, np.ndarray):
            raise TypeError("data должен быть numpy.ndarray")
        if data.ndim not in (1, 2):
            raise ValueError("data должен быть 1D или 2D")
        self._data = data
        self._cursor_index = 0
        self.update(data, 0)

    def update(self, data: Optional[np.ndarray] = None, cursor_index: Optional[int] = None) -> None:  # noqa: D401
        """Обновить отображаемый срез.

        Если `data` не передан, используется ранее установленный через set_data().
        Если `cursor_index` не передан, используется текущий self._cursor_index.
        """
        if data is not None:
            self._data = data
        if self._data is None:
            return
        data = self._data

        if cursor_index is not None:
            self._cursor_index = int(cursor_index)

        if data.ndim == 1:
            n_series, total_len = 1, data.shape[0]
        else:
            n_series, total_len = data.shape[0], data.shape[1]

        start = int(max(0, min(self._cursor_index, max(0, total_len - 1))))
        end = int(min(total_len, start + self._points_per_window))
        if end - start < self._points_per_window:
            start = max(0, end - self._points_per_window)
        self._last_slice = (start, end)

        x = self._x_window

        # Автодобавление недостающих серий
        series_names = list(self._series.keys())
        if n_series > len(series_names):
            for i in range(len(series_names), n_series):
                self.add_series(f"Сигнал {i+1}")
            series_names = list(self._series.keys())

        if n_series == 1:
            y_slice = data[start:end]
            if y_slice.shape[0] != self._points_per_window:
                y_slice = self._fit_to_window(y_slice)
            self._series[series_names[0]].setData(x, y_slice, connect='finite')
        else:
            for i in range(n_series):
                y_slice = data[i, start:end]
                if y_slice.shape[0] != self._points_per_window:
                    y_slice = self._fit_to_window(y_slice)
                self._series[series_names[i]].setData(x, y_slice, connect='finite')

        self.plotItem.setXRange(0.0, self._x_window_seconds, padding=0.0)
        self.plotItem.setYRange(self._y_range[0], self._y_range[1], padding=0.0)

        self.dataUpdated.emit(start, end)

    # ------------- Вспомогательные -------------
    def _fit_to_window(self, y: np.ndarray) -> np.ndarray:
        target = self._points_per_window
        if y.size == 0:
            return np.zeros(target, dtype=float)
        if y.size == target:
            return y
        src_x = np.linspace(0.0, 1.0, y.size)
        dst_x = np.linspace(0.0, 1.0, target)
        return np.interp(dst_x, src_x, y)

    def _on_pan_seconds(self, dx_seconds: float) -> None:
        """Реакция на перетаскивание: преобразуем секунды в точки и сдвигаем курсор."""
        if self._data is None:
            return
        # Переводим смещение в секунды в смещение по индексам
        step_points = int(round(dx_seconds / max(self._dt, 1e-12)))
        if step_points == 0:
            return

        # Положительное dx_seconds (тянем влево) — двигаем курсор вперёд (к большим индексам)
        new_cursor = self._cursor_index + step_points

        # Защита границ
        if self._data.ndim == 1:
            total_len = self._data.shape[0]
        else:
            total_len = self._data.shape[1]
        max_start = max(0, total_len - 1)
        new_cursor = int(max(0, min(new_cursor, max_start)))

        if new_cursor != self._cursor_index:
            self._cursor_index = new_cursor
            self.update()  # перерисуем текущими данными

    # ------------- Контекстное меню (RU) -------------
    def contextMenuEvent(self, event: QtGui.QContextMenuEvent) -> None:  # noqa: N802
        menu = QtWidgets.QMenu(self)
        act_reset = menu.addAction("Сбросить масштаб")
        act_grid_on = menu.addAction("Показать сетку")
        act_grid_off = menu.addAction("Скрыть сетку")
        act_legend_toggle = menu.addAction("Показать/скрыть легенду")
        menu.addSeparator()
        act_save = menu.addAction("Сохранить как изображение…")

        action = menu.exec(event.globalPos())
        if action is None:
            return
        if action == act_reset:
            self.plotItem.enableAutoRange(x=False, y=False)
            self.plotItem.setXRange(0.0, self._x_window_seconds, padding=0.0)
            self.plotItem.setYRange(self._y_range[0], self._y_range[1], padding=0.0)
        elif action == act_grid_on:
            self.set_grid(True)
        elif action == act_grid_off:
            self.set_grid(False)
        elif action == act_legend_toggle:
            self.set_legend(visible=(self._legend is None))
        elif action == act_save:
            self._save_as_image()

    def _save_as_image(self) -> None:
        path, _ = QtWidgets.QFileDialog.getSaveFileName(
            self, "Сохранить как изображение", "график.png", "PNG (*.png);;JPEG (*.jpg *.jpeg)"
        )
        if not path:
            return
        try:
            from pyqtgraph.exporters import ImageExporter
            exporter = ImageExporter(self.plotItem)
            exporter.export(path)
        except Exception as e:  # noqa: BLE001
            QtWidgets.QMessageBox.warning(self, "Ошибка", f"Не удалось сохранить изображение: {e}")


# -----------------------------
# Пример использования (локальный тест)
# -----------------------------
if __name__ == "__main__":
    import sys

    app = QtWidgets.QApplication(sys.argv)

    w = TimeSeriesPlotWidget(
        x_window_seconds=30.0,
        points_per_window=1200,
        y_range=(-2.0, 2.0),
        background="k",
        antialias=True,
        with_legend=True,
    )
    w.resize(1000, 420)
    w.setWindowTitle("Демо: TimeSeriesPlotWidget (PyQt6)")

    # Вторая серия
    w.add_series("Сигнал 2", color="#FFAA00", width=2.0)

    # Демоданные: 2 канала, 10 минут @ 200 Гц
    fs = 200
    duration_sec = 600
    total_len = fs * duration_sec
    t = np.arange(total_len) / fs
    data = np.vstack([
        np.sin(2 * np.pi * 1.0 * t) + 0.1 * np.random.randn(total_len),
        0.5 * np.cos(2 * np.pi * 0.3 * t + 0.5) + 0.1 * np.random.randn(total_len),
    ])

    w.set_data(data)

    # Дополнительно оставим таймер, чтобы имитировать «живое» обновление курсора
    cursor_step = 10

    def on_timer():
        # Двигаем «текущий» курсор вперёд — мышью можно в любой момент двигаться назад
        if w._data is None:
            return
        if w._data.ndim == 1:
            total = w._data.shape[0]
        else:
            total = w._data.shape[1]
        new_c = (w._cursor_index + cursor_step)
        if new_c >= total:
            new_c = 0
        w.update(cursor_index=new_c)

    timer = QtCore.QTimer()
    timer.timeout.connect(on_timer)
    timer.start(50)

    w.show()
    sys.exit(app.exec())
