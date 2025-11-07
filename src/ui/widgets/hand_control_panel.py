from PyQt6.QtCore import Qt
from PyQt6.QtGui import QFont
from PyQt6.QtWidgets import (
    QApplication,
    QDoubleSpinBox,
    QFrame,
    QGridLayout,
    QGroupBox,
    QHBoxLayout,
    QLabel,
    QPushButton,
    QSlider,
    QToolButton,
    QVBoxLayout,
    QWidget,
)
from src.ui.dialogs import (
    HandRegulatorSettingsDialog,
)
import struct

class HandControlPanel(QFrame):
    def __init__(self, parent: QWidget | None = None):
        super().__init__(parent)
        self.model = None
        self.data_set = None

        self.setFrameShape(QFrame.Shape.StyledPanel)
        self.setFrameShadow(QFrame.Shadow.Raised)

        root = QVBoxLayout(self)
        root.setContentsMargins(10, 10, 10, 10)
        root.setSpacing(10)

        root.addWidget(self._build_servo_group())
        root.addWidget(self._build_manual_group())
        root.addWidget(self._build_torque_group())
        root.addStretch(1)

        # Initial state: servo power OFF -> disable direction and run per requirement (1)
        self._apply_enable_rules()

    def config(self, model):
        if model is not None:
            self.model = model
            self.data_set = self.model.realtime_data
            print(f"in hand_control_panel: {self.data_set}")



    # ---------- Группа 1: Сервопривод ----------
    def _build_servo_group(self) -> QGroupBox:
        gb = QGroupBox("Сервопривод")
        lay = QHBoxLayout(gb)
        lay.setContentsMargins(8, 8, 8, 8)

        self.btn_servo_power = QPushButton("Сервопривод ВЫКЛ")
        self.btn_servo_power.setCheckable(True)
        self.btn_servo_power.setFixedSize(140, 32)
        self.btn_servo_power.setStyleSheet(
            """
            QPushButton { background-color: #F1F3F4; border: 1px solid #D0D0D0; border-radius: 6px; }
            QPushButton:checked { background-color: #2ECC71; color: white; }
            """
        )
        self.btn_servo_power.toggled.connect(self._on_servo_power_toggled)

        lay.addWidget(self.btn_servo_power)
        lay.addStretch(1)
        return gb

    # ---------- Группа 2: Ручное управление ----------
    def _build_manual_group(self) -> QGroupBox:
        gb = QGroupBox("Ручное управление сервоприводом")
        grid = QGridLayout(gb)
        grid.setContentsMargins(8, 8, 8, 8)
        grid.setHorizontalSpacing(10)
        grid.setVerticalSpacing(8)

        # Кнопки направления: без фиксации, отдельные обработчики нажатия/отжатия, желтые при нажатии
        self.btn_ccw = QPushButton("Против часовой")
        self.btn_cw = QPushButton("По часовой")

        _dir_btn_css = """
        QPushButton { background-color: #F1F3F4; border: 1px solid #D0D0D0; border-radius: 6px; }
        QPushButton:pressed { background-color: #F4D03F; }  /* желтый при нажатии */
        """
        self.btn_ccw.setStyleSheet(_dir_btn_css)
        self.btn_cw.setStyleSheet(_dir_btn_css)
        self.btn_ccw.setFixedSize(140, 32)
        self.btn_cw.setFixedSize(140, 32)
        self.btn_ccw.setCheckable(False)
        self.btn_cw.setCheckable(False)

        # pressed/released handlers
        self.btn_ccw.pressed.connect(self._on_ccw_pressed)
        self.btn_ccw.released.connect(self._on_ccw_released)
        self.btn_cw.pressed.connect(self._on_cw_pressed)
        self.btn_cw.released.connect(self._on_cw_released)

        row = 0
        hb = QHBoxLayout()
        hb.addWidget(self.btn_ccw)
        hb.addWidget(self.btn_cw)
        hb.addStretch(1)
        grid.addLayout(hb, row, 0, 1, 3)

        # Угловая скорость: поле ввода
        row += 1
        grid.addWidget(QLabel("Угловая скорость"), row, 0, 1, 3)

        row += 1
        self.spin_ang_vel = QDoubleSpinBox()
        self.spin_ang_vel.setRange(0.0, 1.0)
        self.spin_ang_vel.setDecimals(2)
        self.spin_ang_vel.setSingleStep(0.01)
        self.spin_ang_vel.setValue(0.1)
        self.spin_ang_vel.setSuffix(" \u00B0/с")
        self.spin_ang_vel.setFixedHeight(28)
        self.spin_ang_vel.setFixedWidth(100)  # фиксированная ширина 100 px
        self.spin_ang_vel.setFont(QFont("Inconsolata LGC Nerd Font"))
        self.spin_ang_vel.valueChanged.connect(self._on_ang_speed_spin_changed)
        grid.addWidget(self.spin_ang_vel, row, 0, 1, 3)

        # Связанный слайдер (0..100 -> 0.00..1.00)
        row += 1
        self.slider_ang_vel = QSlider(Qt.Orientation.Horizontal)
        self.slider_ang_vel.setRange(0, 100)
        self.slider_ang_vel.setValue(10)
        self.slider_ang_vel.valueChanged.connect(self._on_ang_speed_slider_changed)
        grid.addWidget(self.slider_ang_vel, row, 0, 1, 3)

        return gb

    # ---------- Группа 3: Управление моментом ----------
    def _build_torque_group(self) -> QGroupBox:
        gb = QGroupBox("Управление моментом")
        grid = QGridLayout(gb)
        grid.setContentsMargins(8, 8, 8, 8)
        grid.setHorizontalSpacing(10)
        grid.setVerticalSpacing(8)

        # Общие настройки для спинбоксов этой группы (высота и шрифт)
        def style_spin(sb: QDoubleSpinBox):
            sb.setFixedHeight(28)
            sb.setFixedWidth(100)      # фиксированная ширина 100 px
            sb.setFont(QFont("Inconsolata LGC Nerd Font"))

        row = 0

        # 1) Момент
        grid.addWidget(QLabel("Момент"), row, 0, 1, 3)
        row += 1
        self.spin_torque = QDoubleSpinBox()
        self.spin_torque.setRange(-50.0, 50.0)
        self.spin_torque.setDecimals(1)
        self.spin_torque.setSingleStep(0.1)
        self.spin_torque.setSuffix(" Нм")
        style_spin(self.spin_torque)
        self.spin_torque.valueChanged.connect(self._on_torque_value_changed)
        grid.addWidget(self.spin_torque, row, 0, 1, 3)

        row += 1
        # Слайдер: -500..500 -> -50.0..50.0
        self.slider_torque = QSlider(Qt.Orientation.Horizontal)
        self.slider_torque.setRange(-500, 500)
        self.slider_torque.valueChanged.connect(self._on_torque_slider_changed)
        grid.addWidget(self.slider_torque, row, 0, 1, 3)

        # 2) Скорость нарастания
        row += 1
        grid.addWidget(QLabel("Скорость нарастания"), row, 0, 1, 3)
        row += 1
        self.spin_rate = QDoubleSpinBox()
        self.spin_rate.setRange(0.0, 4.5)
        self.spin_rate.setDecimals(2)
        self.spin_rate.setSingleStep(0.01)
        self.spin_rate.setValue(0.5)
        self.spin_rate.setSuffix(" Нм/с")
        style_spin(self.spin_rate)
        self.spin_rate.valueChanged.connect(self._on_rate_changed)
        grid.addWidget(self.spin_rate, row, 0, 1, 3)

        row += 1
        # Слайдер: 0..450 -> 0.00..4.50
        self.slider_rate = QSlider(Qt.Orientation.Horizontal)
        self.slider_rate.setRange(0, 450)
        self.slider_rate.setValue(50)
        self.slider_rate.valueChanged.connect(self._on_rate_slider_changed)
        grid.addWidget(self.slider_rate, row, 0, 1, 3)

        # 3) Время выдержки
        row += 1
        grid.addWidget(QLabel("Время выдержки"), row, 0, 1, 3)
        row += 1
        self.spin_dwell = QDoubleSpinBox()
        self.spin_dwell.setRange(0.0, 1000.0)
        self.spin_dwell.setDecimals(0)
        self.spin_dwell.setSingleStep(1.0)
        self.spin_dwell.setSuffix(" с")
        style_spin(self.spin_dwell)
        self.spin_dwell.valueChanged.connect(self._on_dwell_changed)
        grid.addWidget(self.spin_dwell, row, 0, 1, 3)

        # 4) Кнопка ПУСК/СТОП
        row += 1
        self.btn_run = QPushButton("ПУСК")
        self.btn_run.setCheckable(True)
        self.btn_run.setFixedSize(140, 32)
        self.btn_run.setStyleSheet(
            """
            QPushButton { background-color: #F1F3F4; border: 1px solid #D0D0D0; border-radius: 6px; }
            QPushButton:checked { background-color: #2ECC71; color: white; }
            """
        )
        self.btn_run.toggled.connect(self._on_run_toggled)
        grid.addWidget(self.btn_run, row, 0, 1, 1)

        # 5) Две QToolButton ниже
        row += 1
        hb = QHBoxLayout()
        self.tbtn1 = QToolButton()
        self.tbtn1.setText("Опция 1")
        self.tbtn1.clicked.connect(self._on_tool_btn1)

        self.tbtn2 = QToolButton()
        self.tbtn2.setText("Опция 2")
        self.tbtn2.clicked.connect(self._on_tool_btn2)

        hb.addWidget(self.tbtn1)
        hb.addWidget(self.tbtn2)
        hb.addStretch(1)
        grid.addLayout(hb, row, 0, 1, 3)

        return gb

    # ---------- Обработчики (заглушки) ----------
    def _on_servo_power_toggled(self, checked: bool):
        self.btn_servo_power.setText("Сервопривод ВКЛ" if checked else "Сервопривод ВЫКЛ")
        print(f"[STUB] Servo power toggled -> {'ON' if checked else 'OFF'}")

        if not checked:
            # При отжатии питания: сброс момента в 0
            self.spin_torque.setValue(0.0)
            self.btn_run.setChecked(False)
            self.model.command_handler.servo_power_off()
        else:
            self.model.command_handler.servo_power_on()
        # Применить правила доступности (блокировка других кнопок виджета)
        self._apply_enable_rules()

    # Раздельные обработчики для кнопок направления
    def _on_ccw_pressed(self):
        print("[STUB] Manual CCW pressed")
        self.model.command_handler.jog_ccw()
        iv = int(1000 * self.spin_ang_vel.value())
        self.model.command_handler.set_plc_register(name='Modbus_VelocitySV', value=iv)

    def _on_ccw_released(self):
        print("[STUB] Manual CCW released")
        self.model.command_handler.halt()
        self.model.command_handler.set_plc_register(name='Modbus_VelocitySV')

    def _on_cw_pressed(self):
        print("[STUB] Manual CW pressed")
        self.model.command_handler.jog_cw()
        iv = int(1000 * self.spin_ang_vel.value())
        self.model.command_handler.set_plc_register(name='Modbus_VelocitySV', value=iv)

    def _on_cw_released(self):
        print("[STUB] Manual CW released")
        self.model.command_handler.halt()
        self.model.command_handler.set_plc_register(name='Modbus_VelocitySV')

    def _on_ang_speed_spin_changed(self, value: float):
        # sync slider (0..100)
        iv = int(round(value * 100))
        if self.slider_ang_vel.value() != iv:
            self.slider_ang_vel.blockSignals(True)
            self.slider_ang_vel.setValue(iv)
            self.slider_ang_vel.blockSignals(False)
        print(f"[STUB] Angular speed spin -> {value:.2f} deg/s")

    def _on_ang_speed_slider_changed(self, ivalue: int):
        v = ivalue / 100.0
        if abs(self.spin_ang_vel.value() - v) > 1e-9:
            self.spin_ang_vel.blockSignals(True)
            self.spin_ang_vel.setValue(v)
            self.spin_ang_vel.blockSignals(False)
        print(f"[STUB] Angular speed slider -> {v:.2f} deg/s")

    def _on_torque_value_changed(self, value: float):
        iv = int(round(value * 10))  # -50..50 -> -500..500
        if self.slider_torque.value() != iv:
            self.slider_torque.blockSignals(True)
            self.slider_torque.setValue(iv)
            self.slider_torque.blockSignals(False)
        print(f"[STUB] Torque spin -> {value:.1f} Nm")

        tv = self.int_to_word(int(500 * self.spin_torque.value()))
        self.model.command_handler.set_plc_register(name='Modbus_TensionSV', value=tv)

    def _on_torque_slider_changed(self, ivalue: int):
        v = ivalue / 10.0
        if abs(self.spin_torque.value() - v) > 1e-9:
            self.spin_torque.blockSignals(True)
            self.spin_torque.setValue(v)
            self.spin_torque.blockSignals(False)
        print(f"[STUB] Torque slider -> {v:.1f} Nm")
        tv = self.int_to_word(int(500 * self.spin_torque.value()))
        self.model.command_handler.set_plc_register(name='Modbus_TensionSV', value=tv)

    def _on_rate_changed(self, value: float):
        iv = int(round(value * 100))  # 0..4.5 -> 0..450
        if self.slider_rate.value() != iv:
            self.slider_rate.blockSignals(True)
            self.slider_rate.setValue(iv)
            self.slider_rate.blockSignals(False)
        print(f"[STUB] Rate spin -> {value:.2f} Nm/s")

    def _on_rate_slider_changed(self, ivalue: int):
        v = ivalue / 100.0
        if abs(self.spin_rate.value() - v) > 1e-9:
            self.spin_rate.blockSignals(True)
            self.spin_rate.setValue(v)
            self.spin_rate.blockSignals(False)
        print(f"[STUB] Rate slider -> {v:.2f} Nm/s")

    def _on_dwell_changed(self, value: float):
        print(f"[STUB] Dwell time -> {value:.0f} s")

    def _on_run_toggled(self, checked: bool):
        self.btn_run.setText("СТОП" if checked else "ПУСК")
        print(f"[STUB] RUN toggled -> {'RUN' if checked else 'STOP'}")
        # Требование (2): при ПУСК нажат — кнопки направления disabled; иначе зависят от питания
        self._apply_enable_rules()
        tv = self.int_to_word(int(500 * self.spin_torque.value()))
        if checked:
            self.model.command_handler.set_plc_register(name='Modbus_TensionSV', value=tv)
            self.model.command_handler.torque_hold()
        else:
            self.model.command_handler.halt()

    def _on_tool_btn1(self):
        print("[STUB] Tool Button 1 clicked")
        HandRegulatorSettingsDialog(self).exec()

    def _on_tool_btn2(self):
        print("[STUB] Tool Button 2 clicked")

    # ---------- Вспомогательное: правила доступности ----------
    def _apply_enable_rules(self):
        power_on = self.btn_servo_power.isChecked()
        running = self.btn_run.isChecked()

        # Пока не нажата кнопка "Сервопривод ..." — неактивны и направления, и ПУСК
        self.btn_run.setEnabled(power_on)
        # При включенном ПУСК — направления неактивны
        enable_dirs = power_on and (not running)
        self.btn_ccw.setEnabled(enable_dirs)
        self.btn_cw.setEnabled(enable_dirs)

    def int_to_word(self, value: int) -> int:
        # Преобразует signed int16 (-32768..32767) в unsigned WORD (0..65535)
        return struct.unpack('>H', struct.pack('>h', value))[0]

# ---------------------- Запуск и проверка ----------------------
if __name__ == "__main__":
    import sys

    app = QApplication(sys.argv)
    w = HandControlPanel()
    w.setWindowTitle("Панель управления сервоприводом — демо")
    w.resize(560, 620)
    w.show()
    sys.exit(app.exec())
