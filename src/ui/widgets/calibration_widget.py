from __future__ import annotations

import os
import typing as t
from dataclasses import dataclass
import numpy as np

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
    QSizePolicy,
)
import yaml  # PyYAML
from src.ui.widgets.time_series_plot_widget import TimeSeriesPlotWidget
from src.ui.calibration_model_coeffs_ui import Ui_coeffs_header
from src.utils.utils import (
    int_to_word,
)
from src.utils.config import (
    Config,
)

CALIB_POINTS = 10
YAML_PATH = "calibration.yaml"
DEFAULT_TORQUES = [0.0, 0.5, 1.0, 2.0, 4.5, 10.0, 15.0, 25.0, 35.0, 50.0]

X_AXIS_RANGE = 30.0
POINTS_PER_WINDOW = 1200

STYLE_SHEET = """
QLabel {
    border: 1px solid #A0A0A0;
    background-color: #FFFFFF;
    font-size: 14px;
    font-family: "Inconsolata LGC Nerd Font", "Segoe UI", Arial, sans-serif;
}
QDoubleSpinBox {
    background-color: #FFFFFF;
    font-size: 14px;
    font-family: "Inconsolata LGC Nerd Font", "Segoe UI", Arial, sans-serif;
}
"""

@dataclass
class CalibPoint:
    index: int
    torque_sv: float = 0.0  # Задание момента в Нм (0..50)
    torque_actual: float = 0.0 # Фактичекское значение датчика момента, Нм
    reference_reading: float = 0.0  # Данные эталоннго динамометра, Н
    reference_torque: float = 0.0 # Пересчитанные данные динамометра, Нм
    fixed: bool = False

class BlinkingMixin:
    """Подсветка/мигание виджета с помощью QTimer и стилей."""

    def __init__(self):
        self._blink_timer: QTimer | None = None
        self._blink_on: bool = False
        self._saved_style: str | None = None

    def start_blink(self, widget: QWidget, color: str = "#32b848"):
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
            f"background-color: {color};" if self._blink_on else (self._saved_style or "")
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
        self.setFrameShape(QFrame.Shape.NoFrame)
        self.setFrameShadow(QFrame.Shadow.Plain)
        self.model = None
        self.data_source = None
        self.config = None

        # Инициализация точек с дефолтными значениями моментов
        self._points: list[CalibPoint] = [
            CalibPoint(i, torque_sv=DEFAULT_TORQUES[i]) for i in range(CALIB_POINTS)
        ]
        self.calib_coeff = {'A1': 0.0, 'B1': 1.0, 'C1': 0.0, 'A2': 1.0, 'B2': 0.0} # Коэффициенты калибровки датчика момента
        self._rows: list[dict[str, QWidget]] = []
        self._active_row_idx: int | None = None
        self.plt_torque = TimeSeriesPlotWidget(
            x_window_seconds=X_AXIS_RANGE,
            y_range=(-50.0, 50.0),
            background="w",
            antialias=True,
            with_legend=True,
        )
        self.coeffs_header = QFrame()
        self._build_ui()
        # self._apply_defaults_to_ui() # Заполнить дефолтные моменты в UI
        self._load_yaml_if_exists()    # Перезаписать значениями из файла (если есть), НЕ блокируя элементы
        self._update_global_state()
        self.timer = QTimer(self)
        self.timer.timeout.connect(self._on_timer)
        self.timer.start(100)

    def _set_model(self, model):
        self.model = model
        self.data_source = self.model.realtime_data

    def _set_config(self, config: Config):
        self.config = config
        if self.config is not None:
            self.calib_coeff = (
                self.config.get("calibration", 'A1'),
                self.config.get("calibration", 'B1'),
                self.config.get("calibration", 'C1'),
                self.config.get("calibration", 'A2'),
                self.config.get("calibration", 'B2'),
            )

    def update_dyno_value(self):
        value = self.model.dyno_data.get_value() / 2.0
        for idx, r in enumerate(self._rows):
            pt = self._points[idx]
            if not pt.fixed:
                r["spn_ref"].setText(f'{value:.2f}')

    def update_torque_value(self):
        value = self.data_source.get_torque()
        self.lbl_torque_val.setText(f'{value:.2f}')
        for idx, r in enumerate(self._rows):
            pt = self._points[idx]
            if not pt.fixed:
                r["torque_val"].setText(f'{value:.2f}')

    def update_plots(self):
        torque_data = self.data_source.torque_data_scaled
        torque_data_indx = self.data_source.head
        self.plt_torque.update(torque_data, torque_data_indx)

    # ----------------------------- UI BUILD ---------------------------------
    def _build_ui(self):
        root = QVBoxLayout(self)
        ch_ui = Ui_coeffs_header()
        ch_ui.setupUi(self.coeffs_header)
        calibre_vbox = QVBoxLayout()
        calibre_hbox = QHBoxLayout()
        servo_hbox = QHBoxLayout()
        points_layout = QVBoxLayout()
        plot_layout = QVBoxLayout()
        #self.plt_torque.setFixedSize(800, 380)  # фиксируем виджет
        #self.plt_torque.setSizePolicy(QSizePolicy.Policy.Fixed, QSizePolicy.Policy.Fixed)
        self.plt_torque.set_axis_labels(y_label="Крутящий момент, Нм")
        points_layout.addWidget(self._make_calibration_group_v2())
        points_layout.addSpacing(40)
        plot_layout.addSpacing(20)
        plot_layout.addWidget(self.plt_torque)

        calibre_vbox.addWidget(self.coeffs_header)
        calibre_vbox.addLayout(points_layout)

        calibre_hbox.addLayout(calibre_vbox)
        calibre_hbox.addLayout(plot_layout)
        # calibre_hbox.addSpacing(500)
        servo_hbox.addWidget(self._make_servo_group())
        # servo_hbox.addStretch(1)
        servo_hbox.addStretch(1)
        # root.addWidget(self.coeffs_header)
        root.addLayout(calibre_hbox)
        root.addLayout(servo_hbox)
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
        self.btn_cw.pressed.connect(self._on_servo_cw_pressed)
        self.btn_cw.released.connect(self._on_servo_cw_released)
        self.btn_ccw.clicked.connect(self._on_servo_ccw)
        self.btn_ccw.pressed.connect(self._on_servo_ccw_pressed)
        self.btn_ccw.released.connect(self._on_servo_ccw_released)
        self.btn_zero_angle.clicked.connect(self._on_zero_angle)
        self.btn_zero_torque.clicked.connect(self._on_zero_torque)

        # Задание скорости
        speed_lbl = QLabel("Скорость (град/с):")
        self.speed_slider = QSlider(Qt.Orientation.Horizontal)
        self.speed_slider.setRange(0, 100)
        self.speed_slider.setValue(25)

        self.speed_spin = QDoubleSpinBox()
        self.speed_spin.setRange(0.0, 1.0)
        self.speed_spin.setDecimals(2)
        self.speed_spin.setSingleStep(0.01)
        self.speed_spin.setSuffix(" град/с")
        self.speed_spin.setValue(0.1)
        self.speed_spin.setStyleSheet(STYLE_SHEET)

        # Связка значений спинбокса и слайдера
        self.speed_slider.valueChanged.connect(self._sync_speed_from_slider)
        self.speed_spin.valueChanged.connect(self._sync_speed_from_spin)

        # Индикаторы (заглушки)
        self.lbl_angle_val = QLabel('0.00 \u00B0')
        self.lbl_torque_val = QLabel('0.00 Нм')
        self.lbl_angle_val.setObjectName("value_label")
        self.lbl_torque_val.setObjectName("value_label")
        self.lbl_angle_val.setStyleSheet(
            "border: 1px solid #E0E0E0;"
            "background-color: #FFFFFF;"
            "font-size: 14px;"
            "font-family: 'Inconsolata LGC Nerd Font', 'Segoe UI', Arial, sans-serif;"
        )
        self.lbl_torque_val.setStyleSheet(
            "border: 1px solid #E0E0E0;"
            "background-color: #FFFFFF;"
            "font-size: 14px;"
            "font-family: 'Inconsolata LGC Nerd Font', 'Segoe UI', Arial, sans-serif;"
        )

        dummy = QLabel()

        btn_width = 125
        btn_height = 26

        # Размеры и пропорции
        self.btn_cw.setFixedSize(btn_width, btn_height)  # фиксируем виджет
        self.btn_cw.setSizePolicy(QSizePolicy.Policy.Fixed, QSizePolicy.Policy.Fixed)
        self.btn_ccw.setFixedSize(btn_width, btn_height)  # фиксируем виджет
        self.btn_ccw.setSizePolicy(QSizePolicy.Policy.Fixed, QSizePolicy.Policy.Fixed)
        self.btn_zero_angle.setFixedSize(btn_width, btn_height)  # фиксируем виджет
        self.btn_zero_angle.setSizePolicy(QSizePolicy.Policy.Fixed, QSizePolicy.Policy.Fixed)
        self.btn_zero_torque.setFixedSize(btn_width, btn_height)  # фиксируем виджет
        self.btn_zero_torque.setSizePolicy(QSizePolicy.Policy.Fixed, QSizePolicy.Policy.Fixed)
        self.lbl_angle_val.setFixedSize(btn_width, btn_height)  # фиксируем виджет
        self.lbl_angle_val.setSizePolicy(QSizePolicy.Policy.Fixed, QSizePolicy.Policy.Fixed)
        self.lbl_torque_val.setFixedSize(btn_width, btn_height)  # фиксируем виджет
        self.lbl_torque_val.setSizePolicy(QSizePolicy.Policy.Fixed, QSizePolicy.Policy.Fixed)
        self.speed_slider.setFixedSize(btn_width, btn_height)  # фиксируем виджет
        self.speed_slider.setSizePolicy(QSizePolicy.Policy.Fixed, QSizePolicy.Policy.Fixed)
        # dummy.setFixedSize(btn_width, btn_height)  # фиксируем виджет
        dummy.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Expanding)

        # Компоновка
        layout.addWidget(self.btn_cw, 0, 0)
        layout.addWidget(self.btn_ccw, 0, 1)
        layout.addWidget(speed_lbl, 0, 2)
        layout.addWidget(self.speed_spin, 1, 2)
        layout.addWidget(self.speed_slider, 2, 2)
        layout.addWidget(self.btn_zero_angle, 2, 1)
        layout.addWidget(self.btn_zero_torque, 1, 1)
        layout.addWidget(self.lbl_torque_val, 1, 0)
        layout.addWidget(self.lbl_angle_val, 2, 0)
        layout.addWidget(dummy, 0, 3)
        layout.addWidget(dummy, 1, 3)
        layout.addWidget(dummy, 2, 3)

        return gb

    # ---- CALIBRATION GROUP --------------------------------------------------
    def _make_calibration_group_v2(self) -> QGroupBox:
        gb = QGroupBox("Калибровка датчика момента")
        layout = QGridLayout(gb)

        caption = [
            QLabel(" "),
            QLabel("Заданный момент, Нм"),
            QLabel("Фактический момент, Нм"),
            QLabel("Эталонный динамометр, Н"),
            QLabel("Эталонный момент, Нм"),
            QLabel(" ")
        ]
        for i, text in enumerate(caption):
            caption[i].setAlignment(Qt.AlignmentFlag.AlignCenter)
            layout.addWidget(text, 0, i)

        for i in range(CALIB_POINTS):
            row_widgets: dict[str, QWidget] = {}
            row = i + 1

            # Метка индекса
            lbl_idx = QLabel(f"{row}")
            lbl_idx.setAlignment(Qt.AlignmentFlag.AlignCenter)
            lbl_idx.setFixedSize(40, 25)  # фиксируем виджет
            lbl_idx.setSizePolicy(QSizePolicy.Policy.Fixed, QSizePolicy.Policy.Fixed)
            row_widgets["lbl_idx"] = lbl_idx

            # Уставка момента, Нм
            spn_torque = QDoubleSpinBox()
            spn_torque.setAlignment(Qt.AlignmentFlag.AlignRight)
            spn_torque.setRange(0, 55.0)
            spn_torque.setDecimals(2)
            spn_torque.setSingleStep(0.1)
            spn_torque.setStyleSheet(STYLE_SHEET)
            spn_torque.valueChanged.connect(lambda val, idx=i: self._on_value_changed(val, idx))
            row_widgets["torque_sv"] = spn_torque

            # Фактическое значение датчика момента, Нм
            lbl_torque = QLabel('0.00')
            lbl_torque.setAlignment(Qt.AlignmentFlag.AlignRight)
            lbl_torque.setStyleSheet(STYLE_SHEET)
            row_widgets["torque_val"] = lbl_torque

            # Данные эталонного динамометра, Н
            spn_ref = QLabel('0.0')
            spn_ref.setAlignment(Qt.AlignmentFlag.AlignRight)
            spn_ref.setStyleSheet(STYLE_SHEET)
            row_widgets["spn_ref"] = spn_ref

            # Эталонный момент, Нм
            lbl_ref_torque = QLabel('0.00')
            lbl_ref_torque.setAlignment(Qt.AlignmentFlag.AlignRight)
            lbl_ref_torque.setStyleSheet(STYLE_SHEET)
            row_widgets["ref_torque_val"] = lbl_ref_torque

            # Кнопка задания/фиксации
            btn_set = QPushButton("Задать")
            btn_set.clicked.connect(lambda _, idx=i: self._on_point_set_clicked(idx))
            row_widgets["btn_set"] = btn_set

            layout.addWidget(lbl_idx, row, 0)
            layout.addWidget(spn_torque, row, 1)
            layout.addWidget(lbl_torque, row, 2)
            layout.addWidget(spn_ref, row, 3)
            layout.addWidget(lbl_ref_torque, row, 4)
            layout.addWidget(btn_set, row, 5)

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
            torque_sv: QDoubleSpinBox = t.cast(QDoubleSpinBox, row["torque_sv"])  # type: ignore
            torque_sv.setValue(pt.torque_sv)

    # ----------------------- EVENT HANDLERS ----------------------------------
    # --- Servo controls ---
    def _on_servo_cw(self):
        print("[STUB] Servo CW clicked")

    def _on_servo_cw_pressed(self):
        print("[STUB] Servo CW pressed")
        self.model.command_handler.jog_cw()
        iv = 200
        self.model.command_handler.set_plc_register(name='Modbus_VelocitySV', value=iv)

    def _on_servo_cw_released(self):
        print("[STUB] Servo CW released")
        self.model.command_handler.halt()
        self.model.command_handler.set_plc_register(name='Modbus_VelocitySV')

    def _on_servo_ccw(self):
        print("[STUB] Servo CCW clicked")

    def _on_servo_ccw_pressed(self):
        print("[STUB] Servo CCW pressed")
        self.model.command_handler.jog_ccw()
        iv = 200
        self.model.command_handler.set_plc_register(name='Modbus_VelocitySV', value=iv)

    def _on_servo_ccw_released(self):
        print("[STUB] Servo CCW released")
        self.model.command_handler.halt()
        self.model.command_handler.set_plc_register(name='Modbus_VelocitySV')

    def _on_speed_changed(self, val: int):
        print(f"[STUB] Speed set to {val}")

    def _sync_speed_from_slider(self, v: int):
        # синхронизируем спинбокс, затем вызываем ваш существующий обработчик скорости
        if int(self.speed_spin.value())*100 != v:
            self.speed_spin.blockSignals(True)
            self.speed_spin.setValue(float(v)/100.0)
            self.speed_spin.blockSignals(False)
        self._on_speed_changed(v)

    def _sync_speed_from_spin(self, v: float):
        iv = int(round(v*100.0))
        if self.speed_slider.value() != iv:
            self.speed_slider.blockSignals(True)
            self.speed_slider.setValue(iv)
            self.speed_slider.blockSignals(False)
        self._on_speed_changed(iv)

    def _on_zero_angle(self):
        print("[STUB] Zero current angle")
        self.lbl_angle_val.setText("0.00 \u00B0")

    def _on_zero_torque(self):
        print("[STUB] Zero current torque")
        self.lbl_torque_val.setText("0.00 Нм")

    # --- Calibration logic ---
    def _on_point_set_clicked(self, idx: int):
        row = self._rows[idx]
        pt = self._points[idx]
        btn: QPushButton = t.cast(QPushButton, row["btn_set"])  # type: ignore
        torque_sv: QDoubleSpinBox = t.cast(QDoubleSpinBox, row["torque_sv"])  # type: ignore
        # spn_ref: QDoubleSpinBox = t.cast(QDoubleSpinBox, row["spn_ref"])  # type: ignore

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
            self.start_blink(widget=row.get("btn_set"))
            # Стартуем работу сервопривоода в режиме ПИД регулирования по моменту
            tv = int_to_word(int(500 * torque_sv.value()))
            self.model.command_handler.set_plc_register(name='Modbus_TensionSV', value=tv)
            self.model.command_handler.torque_hold()
        elif self._active_row_idx == idx:
            self.model.command_handler.halt()
            # Фиксация значений
            pt.torque_sv = torque_sv.value()
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

    def _on_value_changed(self, value: float, idx: int):
        row = self._rows[idx]
        self._points[idx].torque_sv = value
        self._save_yaml()

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
        # Расчёт коэффициентов и сохранение в YAML

        x, y = self.get_xy_arrays()
        # Массив точек нижнего поддиапазона
        x_l, y_l = (x[:6], y[:6])
        if np.unique(x_l).size < 3:
            QMessageBox.information(
                self,
                "Предупреждение:",
                "Недостаточно уникальных значений для расчета коэффициентов!\nНачните процедуру калибровки заново",
            )
            return
        # Массив точек верхнего поддиапазона
        x_h, y_h = (x[5:], y[5:])
        # Аппроксимация полиномом 2-го порядка
        coeffs_l = np.polyfit(x,y,2) # np.polyfit(x_l, y_l, 2)
        A1, B1, C1 = tuple(float(c) for c in coeffs_l)  # коэффициенты полинома y = Ax^2 + Bx + C
        self.config.cfg["calibration"]["A1"] = A1
        self.config.cfg["calibration"]["B1"] = B1
        self.config.cfg["calibration"]["C1"] = C1
        # Аппроксимация полиномом 1-го порядка
        coeffs_h = np.polyfit(x_l, y_l, 1)
        A2, B2 = tuple(float(c) for c in coeffs_h)  # коэффициенты полинома y = Ax + B
        self.config.cfg["calibration"]["A2"] = A2
        self.config.cfg["calibration"]["B2"] = B2

        print(f"A={A1}, B={B1}, C={C1}")
        print(f"A={A2}, B={B2}")
        self.config.save()

        self._save_yaml()
        QMessageBox.information(
            self,
            "Расчёт завершён",
            "Расчёт калибровочных коэффициентов выполнен. Данные сохранены в файле конфигурации и в ПЛК",
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
                if "torque_sv" in pd:
                    pt.torque_sv = float(pd.get("torque_sv", pt.torque_sv))
                if "torque_actual" in pd:
                    pt.torque_actual = float(pd.get("torque_actual", pt.torque_actual))
                if "reference_reading" in pd:
                    pt.reference_torque = float(pd.get("reference_reading", pt.reference_reading))
                if "reference_torque" in pd:
                    pt.reference_torque = float(pd.get("reference_torque", pt.reference_torque))
                # Фиксацию не переносим — новая калибровка может начаться сразу
                pt.fixed = False

            # Применяем к UI (поля активны)
            for i, pt in enumerate(self._points):
                row = self._rows[i]
                torque_sv: QDoubleSpinBox = t.cast(QDoubleSpinBox, row["torque_sv"])  # type: ignore
                torque_actual: QLabel = t.cast(QLabel, row["torque_val"]) # type: ignore
                spn_ref: QLabel = t.cast(QLabel, row["spn_ref"])  # type: ignore
                ref_torque_val: QLabel = t.cast(QLabel, row["ref_torque_val"])
                torque_sv.setValue(pt.torque_sv)
                torque_actual.setText(f'{pt.torque_actual:.2f}')
                spn_ref.setText(f'{pt.reference_reading:.2f}')
                ref_torque_val.setText(f'{pt.reference_torque:.2f}')

        except Exception as exc:
            QMessageBox.warning(self, "Ошибка загрузки", f"Не удалось загрузить {YAML_PATH}: {exc}")

    def _save_yaml(self):
        if not yaml:
            QMessageBox.warning(self, "PyYAML недоступен", "Модуль PyYAML не найден — сохранение пропущено.")
            return
        # todo: _save_yaml data
        data = {
            "points": [
                {
                    "index": p.index,
                    "torque_sv": p.torque_sv,
                    "torque_actual": p.torque_actual,
                    "reference_reading": p.reference_reading,
                    "reference_torque": p.reference_torque,
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

    def get_xy_arrays(self):
        # Извлечение фактического и эталонного момента в отдельные списки
        # x_list = [pt.torque_actual for pt in self._points]
        x_list = [pt.torque_sv for pt in self._points]
        y_list = [pt.reference_torque for pt in self._points]

        # Преобразование списков в numpy массивы
        x = np.array(x_list)
        y = np.array(y_list)
        return x, y

    def _on_timer(self):
        self.update_dyno_value()
        self.update_torque_value()
        self.update_plots()

# ------------------------------- DEMO APP -----------------------------------
if __name__ == "__main__":
    import sys

    app = QApplication(sys.argv)
    w = ServoCalibrationWidget()
    w.setWindowTitle("Калибровка датчика момента — демо")
    w.resize(900, 520)
    w.show()
    sys.exit(app.exec())
