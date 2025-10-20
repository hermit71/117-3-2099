from __future__ import annotations

import os
import typing as t
from dataclasses import dataclass

from PyQt6.QtCore import Qt, QTimer
from PyQt6.QtWidgets import (
    QApplication,
    QDoubleSpinBox,
    QFrame,
    QGridLayout,
    QGroupBox,
    QHBoxLayout,
    QLabel,
    QMessageBox,
    QPushButton,
    QSlider,
    QVBoxLayout,
    QWidget,
)

try:
    import yaml  # PyYAML
except Exception:  # pragma: no cover
    yaml = None


CALIB_POINTS = 10
YAML_PATH = "calibration.yaml"
DEFAULT_TORQUES = [0.0, 0.5, 1.0, 2.0, 4.5, 10.0, 15.0, 25.0, 35.0, 50.0]


@dataclass
class CalibPoint:
    index: int
    commanded_torque: float = 0.0  # Нм (0..50)
    reference_reading: float = 0.0  # произв. ед. эталонного датчика
    fixed: bool = False


class BlinkingMixin:
    """Подсветка/мигание виджета с помощью QTimer и стилей."""

    def __init__(self):
        self._blink_timer: QTimer | None = None
        self._blink_on: bool = False
        self._saved_style: str | None = None

    def start_blink(self, widget: QWidget, color: str = "#FFF3CD"):
        if self._blink_timer is None:
            self._blink_timer = QTimer(widget)
            self._blink_timer.timeout.connect(lambda: self._toggle_blink(widget, color))
            self._blink_timer.start(450)
            self._saved_style = widget.styleSheet()

    def stop_blink(self, widget: QWidget):
        if self._blink_timer is not None:
            self._blink_timer.stop()
            self._blink_timer.deleteLater()
            self._blink_timer = None
        self._blink_on = False
        if self._saved_style is not None:
            widget.setStyleSheet(self._saved_style)
            self._saved_style = None

    def _toggle_blink(self, widget: QWidget, color: str):
        self._blink_on = not self._blink_on
        widget.setStyleSheet(
            f"background-color: {color}; border-radius: 6px;" if self._blink_on else (self._saved_style or "")
        )


class ServoCalibrationWidget(QFrame, BlinkingMixin):
    """
    Виджет (QFrame), содержащий:
      1) Группу управления сервоприводом (кнопки/индикаторы, обработчики-заглушки).
      2) Группу калибровки датчика момента на 10 точек, с логикой блокировок и подсветкой активной точки.

    Новая калибровка доступна в любой момент (кнопка «Новая калибровка»).
    При наличии файла calibration.yaml значения подставляются, но поля и кнопки остаются активными.
    «Расчёт коэффициентов» активируется, когда все точки зафиксированы.
    Обработчики — заглушки без реальной логики.
    """

    def __init__(self, parent: QWidget | None = None):
        super().__init__(parent)
        BlinkingMixin.__init__(self)
        self.setFrameShape(QFrame.Shape.StyledPanel)
        self.setFrameShadow(QFrame.Shadow.Raised)

        # Инициализация точек с дефолтными значениями моментов
        self._points: list[CalibPoint] = [
            CalibPoint(i, commanded_torque=DEFAULT_TORQUES[i - 1]) for i in range(1, CALIB_POINTS + 1)
        ]
        self._rows: list[dict[str, QWidget]] = []
        self._active_row_idx: int | None = None

        self._build_ui()
        self._apply_defaults_to_ui()  # Заполнить дефолтные моменты в UI
        self._load_yaml_if_exists()   # Перезаписать значениями из файла (если есть), НЕ блокируя элементы
        self._update_global_state()

    # ----------------------------- UI BUILD ---------------------------------
    def _build_ui(self):
        root = QVBoxLayout(self)
        root.addWidget(self._make_servo_group())
        root.addWidget(self._make_calibration_group())
        root.addStretch(1)

    # ---- SERVO GROUP --------------------------------------------------------
    def _make_servo_group(self) -> QGroupBox:
        gb = QGroupBox("Управление сервоприводом")
        layout = QGridLayout(gb)

        # Кнопки направления
        self.btn_cw = QPushButton("По часовой")
        self.btn_ccw = QPushButton("Против часовой")
        self.btn_zero_angle = QPushButton("Обнулить угол")
        self.btn_zero_torque = QPushButton("Обнулить момент")

        self.btn_cw.clicked.connect(self._on_servo_cw)
        self.btn_ccw.clicked.connect(self._on_servo_ccw)
        self.btn_zero_angle.clicked.connect(self._on_zero_angle)
        self.btn_zero_torque.clicked.connect(self._on_zero_torque)

        # Задание скорости
        speed_lbl = QLabel("Скорость:")
        self.speed_slider = QSlider(Qt.Orientation.Horizontal)
        self.speed_slider.setRange(0, 100)
        self.speed_slider.setValue(25)
        self.speed_slider.valueChanged.connect(self._on_speed_changed)

        # Контроль угла (задание/переход)
        angle_lbl = QLabel("Задать угол, °:")
        self.angle_spin = QDoubleSpinBox()
        self.angle_spin.setRange(-180.0, 180.0)
        self.angle_spin.setDecimals(2)
        self.angle_spin.setSingleStep(0.5)
        self.btn_set_angle = QPushButton("Перейти к углу")
        self.btn_set_angle.clicked.connect(self._on_set_angle)

        # Индикаторы (заглушки)
        self.lbl_angle_val = QLabel("Текущий угол: — °")
        self.lbl_torque_val = QLabel("Текущий момент: — Нм")

        # Компоновка
        layout.addWidget(self.btn_cw, 0, 0)
        layout.addWidget(self.btn_ccw, 0, 1)
        layout.addWidget(speed_lbl, 1, 0)
        layout.addWidget(self.speed_slider, 1, 1)
        layout.addWidget(angle_lbl, 2, 0)
        layout.addWidget(self.angle_spin, 2, 1)
        layout.addWidget(self.btn_set_angle, 2, 2)
        layout.addWidget(self.btn_zero_angle, 0, 2)
        layout.addWidget(self.btn_zero_torque, 0, 3)
        layout.addWidget(self.lbl_angle_val, 3, 0, 1, 2)
        layout.addWidget(self.lbl_torque_val, 3, 2, 1, 2)

        return gb

    # ---- CALIBRATION GROUP --------------------------------------------------
    def _make_calibration_group(self) -> QGroupBox:
        gb = QGroupBox("Калибровка датчика момента (10 точек)")
        layout = QGridLayout(gb)

        # Заголовки
        layout.addWidget(QLabel("Точка"), 0, 0)
        layout.addWidget(QLabel("Заданный момент, Нм (0–50)"), 0, 1)
        layout.addWidget(QLabel("Показание эталонного датчика"), 0, 2)
        layout.addWidget(QLabel("Действие"), 0, 3)

        for i in range(CALIB_POINTS):
            row_widgets: dict[str, QWidget] = {}
            row = i + 1

            # Метка индекса
            lbl_idx = QLabel(f"{row}")
            lbl_idx.setAlignment(Qt.AlignmentFlag.AlignCenter)
            row_widgets["lbl_idx"] = lbl_idx

            # Ввод момента
            spn_torque = QDoubleSpinBox()
            spn_torque.setRange(0.0, 50.0)
            spn_torque.setDecimals(2)
            spn_torque.setSingleStep(0.1)
            row_widgets["spn_torque"] = spn_torque

            # Ввод эталонного показания
            spn_ref = QDoubleSpinBox()
            spn_ref.setRange(-1e6, 1e6)
            spn_ref.setDecimals(4)
            spn_ref.setSingleStep(0.01)
            row_widgets["spn_ref"] = spn_ref

            # Кнопка задания/фиксации
            btn_set = QPushButton("Задать")
            btn_set.clicked.connect(lambda _, idx=i: self._on_point_set_clicked(idx))
            row_widgets["btn_set"] = btn_set

            layout.addWidget(lbl_idx, row, 0)
            layout.addWidget(spn_torque, row, 1)
            layout.addWidget(spn_ref, row, 2)
            layout.addWidget(btn_set, row, 3)

            self._rows.append(row_widgets)

        # Нижняя панель управления калибровкой
        bottom_row = QHBoxLayout()
        self.btn_new_calib = QPushButton("Новая калибровка (сброс фиксации)")
        self.btn_new_calib.clicked.connect(self._on_new_calibration)
        self.btn_compute = QPushButton("Расчёт калибровочных коэффициентов")
        self.btn_compute.setEnabled(False)
        self.btn_compute.clicked.connect(self._on_compute_clicked)
        bottom_row.addWidget(self.btn_new_calib)
        bottom_row.addWidget(self.btn_compute)

        layout.addLayout(bottom_row, CALIB_POINTS + 1, 0, 1, 4)

        return gb

    # ------------------------ DEFAULTS TO UI --------------------------------
    def _apply_defaults_to_ui(self):
        for i, pt in enumerate(self._points):
            row = self._rows[i]
            spn_torque: QDoubleSpinBox = t.cast(QDoubleSpinBox, row["spn_torque"])  # type: ignore
            spn_torque.setValue(pt.commanded_torque)

    # ---------------------------- EVENT HANDLERS (STUBS) --------------------
    # --- Servo controls ---
    def _on_servo_cw(self):
        print("[STUB] Servo CW pressed")

    def _on_servo_ccw(self):
        print("[STUB] Servo CCW pressed")

    def _on_speed_changed(self, val: int):
        print(f"[STUB] Speed set to {val}")

    def _on_set_angle(self):
        angle = self.angle_spin.value()
        print(f"[STUB] Set angle requested: {angle} deg")

    def _on_zero_angle(self):
        print("[STUB] Zero current angle")
        self.lbl_angle_val.setText("Текущий угол: 0.00 °")

    def _on_zero_torque(self):
        print("[STUB] Zero current torque")
        self.lbl_torque_val.setText("Текущий момент: 0.00 Нм")

    # --- Calibration logic ---
    def _on_point_set_clicked(self, idx: int):
        row = self._rows[idx]
        pt = self._points[idx]
        btn: QPushButton = t.cast(QPushButton, row["btn_set"])  # type: ignore
        spn_torque: QDoubleSpinBox = t.cast(QDoubleSpinBox, row["spn_torque"])  # type: ignore
        spn_ref: QDoubleSpinBox = t.cast(QDoubleSpinBox, row["spn_ref"])  # type: ignore

        if pt.fixed:
            # Уже зафиксировано — предлагаем перезаписать при повторном нажатии
            # Для новой калибровки можно нажать «Новая калибровка», либо перезаписать точку.
            pass

        if self._active_row_idx is None:
            # Переход в режим задания для этой строки
            self._active_row_idx = idx
            btn.setText("Зафиксировать")
            self._set_other_rows_enabled(False, except_idx=idx)
            # Включаем мигание всей строки
            self.start_blink(row_widget := row.get("row_widget") or QWidget())
        elif self._active_row_idx == idx:
            # Фиксация значений
            torque = spn_torque.value()
            if not (0.0 <= torque <= 50.0):
                QMessageBox.warning(self, "Ошибка", "Момент должен быть в диапазоне 0..50 Нм")
                return

            pt.commanded_torque = torque
            pt.reference_reading = spn_ref.value()
            pt.fixed = True

            btn.setText("Задать")
            self.stop_blink(row.get("row_widget") or QWidget())
            self._active_row_idx = None
            self._set_other_rows_enabled(True)
            self._update_global_state()
        else:
            # Другая точка уже активна
            QMessageBox.information(
                self,
                "Другой пункт активен",
                f"Сначала зафиксируйте точку {self._points[self._active_row_idx].index}.",
            )

    def _set_other_rows_enabled(self, enabled: bool, except_idx: int | None = None):
        for i, row in enumerate(self._rows):
            if except_idx is not None and i == except_idx:
                continue
            btn: QPushButton = t.cast(QPushButton, row["btn_set"])  # type: ignore
            # По требованию ТЗ — кнопки всегда могут быть активными для новой калибровки,
            # но на время активной точки остальные блокируем.
            btn.setEnabled(enabled)

    def _on_new_calibration(self):
        """Сброс фиксации всех точек: элементы становятся активными и доступны для новой калибровки."""
        if self._active_row_idx is not None:
            # Остановить мигание активной строки
            row = self._rows[self._active_row_idx]
            self.stop_blink(row.get("row_widget") or QWidget())
        self._active_row_idx = None

        for i, pt in enumerate(self._points):
            pt.fixed = False
            row = self._rows[i]
            btn: QPushButton = t.cast(QPushButton, row["btn_set"])  # type: ignore
            btn.setEnabled(True)
            btn.setText("Задать")
        self._update_global_state()

    def _update_global_state(self):
        all_fixed = all(p.fixed for p in self._points)
        self.btn_compute.setEnabled(all_fixed)

    def _on_compute_clicked(self):
        # Заглушка: здесь бы происходил расчёт коэффициентов и сохранение YAML
        self._save_yaml()
        QMessageBox.information(
            self,
            "Расчёт завершён",
            "[STUB] Расчёт калибровочных коэффициентов выполнен. Данные сохранены в calibration.yaml",
        )

    # ----------------------------- YAML I/O ----------------------------------
    def _load_yaml_if_exists(self):
        """
        При наличии YAML: подставляем значения моментов/эталона из файла.
        Поля ввода и кнопки остаются АКТИВНЫМИ. Флаги fixed сбрасываются (новая калибровка доступна сразу).
        """
        if not yaml or not os.path.exists(YAML_PATH):
            return
        try:
            with open(YAML_PATH, "r", encoding="utf-8") as f:
                data = yaml.safe_load(f) or {}
            points = data.get("points", [])
            for i, pd in enumerate(points[:CALIB_POINTS]):
                pt = self._points[i]
                # Перезаписываем значениями из файла (если пользователь вводил другие)
                if "commanded_torque" in pd:
                    pt.commanded_torque = float(pd.get("commanded_torque", pt.commanded_torque))
                if "reference_reading" in pd:
                    pt.reference_reading = float(pd.get("reference_reading", pt.reference_reading))
                # Фиксацию не переносим — новая калибровка может начаться сразу
                pt.fixed = False

            # Применяем к UI (поля активны)
            for i, pt in enumerate(self._points):
                row = self._rows[i]
                spn_torque: QDoubleSpinBox = t.cast(QDoubleSpinBox, row["spn_torque"])  # type: ignore
                spn_ref: QDoubleSpinBox = t.cast(QDoubleSpinBox, row["spn_ref"])  # type: ignore
                spn_torque.setValue(pt.commanded_torque)
                spn_ref.setValue(pt.reference_reading)
        except Exception as exc:
            QMessageBox.warning(self, "Ошибка загрузки", f"Не удалось загрузить {YAML_PATH}: {exc}")

    def _save_yaml(self):
        if not yaml:
            QMessageBox.warning(self, "PyYAML недоступен", "Модуль PyYAML не найден — сохранение пропущено.")
            return
        data = {
            "points": [
                {
                    "index": p.index,
                    "commanded_torque": p.commanded_torque,
                    "reference_reading": p.reference_reading,
                    "fixed": p.fixed,
                }
                for p in self._points
            ]
        }
        try:
            with open(YAML_PATH, "w", encoding="utf-8") as f:
                yaml.safe_dump(data, f, allow_unicode=True, sort_keys=False)
        except Exception as exc:
            QMessageBox.warning(self, "Ошибка сохранения", f"Не удалось сохранить {YAML_PATH}: {exc}")


# ------------------------------- DEMO APP -----------------------------------
if __name__ == "__main__":
    import sys

    app = QApplication(sys.argv)
    w = ServoCalibrationWidget()
    w.setWindowTitle("Калибровка датчика момента — демо")
    w.resize(900, 520)
    w.show()
    sys.exit(app.exec())
