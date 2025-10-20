"""Главное окно приложения: загрузка интерфейса и привязка логики."""

from __future__ import annotations

import logging
from dataclasses import dataclass

from PyQt6.QtCore import Qt, pyqtSlot as Slot
from PyQt6.QtWidgets import (
    QApplication,
    QMainWindow,
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

from src.data.model import Model
from  src.models.modeldata import ModbusDataSource
from src.ui.designer_loader import load_ui
from src.ui.dialogs import (
    AboutDialog,
    ConnectionSettingsDialog,
    GeneralSettingsDialog,
    GraphSettingsDialog,
    HandRegulatorSettingsDialog,
)
from src.ui.widgets import dashboards, connection_control_widget as cw
from src.utils.config import Config

logger = logging.getLogger(__name__)

from typing import TYPE_CHECKING, cast, Iterable, List

@dataclass
class ControlButtons:
    """Группа кнопок управления испытанием."""

    start: QPushButton
    pause: QPushButton
    stop: QPushButton
    emergency_reset: QPushButton

    def setup(self) -> None:
        """Настроить внешний вид и базовое состояние кнопок."""

        self.start.setCheckable(True)
        self.pause.setCheckable(True)
        self.pause.setEnabled(False)

        self.start.setStyleSheet(
            """
            QPushButton:checked {
                background-color: #4caf50;
                color: white;
            }
            """
        )
        self.pause.setStyleSheet(
            """
            QPushButton:checked {
                background-color: #f9f2a8;
                color: black;
            }
            """
        )

    def ensure_start_checked(self) -> None:
        """Оставить кнопку «Старт» в нажатом состоянии."""

        self.start.blockSignals(True)
        self.start.setChecked(True)
        self.start.blockSignals(False)

    def enable_pause(self) -> None:
        """Активировать кнопку паузы и сбросить её состояние."""

        self.pause.setEnabled(True)
        self.pause.blockSignals(True)
        self.pause.setChecked(False)
        self.pause.blockSignals(False)

    def disable_pause(self) -> None:
        """Отключить кнопку паузы и сбросить флажок."""

        self.pause.blockSignals(True)
        self.pause.setChecked(False)
        self.pause.blockSignals(False)
        self.pause.setEnabled(False)

    def reset(self) -> None:
        """Вернуть кнопки управления в исходное состояние."""

        self.start.blockSignals(True)
        self.pause.blockSignals(True)
        self.start.setChecked(False)
        self.pause.setChecked(False)
        self.start.blockSignals(False)
        self.pause.blockSignals(False)
        self.pause.setEnabled(False)


class MainWindow(QMainWindow):
    """Главное окно приложения, координирующее работу всех экранов."""

    def __init__(self, config: Config) -> None:
        super().__init__()
        self.config = config
        load_ui(self, "main_window_view.ui")
        self._setup_menu()

        self.model = Model(self.config)
        self.data_source = ModbusDataSource(self.config.cfg)

        self.command_handler = self.model.command_handler
        self.connection_ctrl = cw.ConnectionControl()
        self.control_buttons = ControlButtons(
            start=self.btnStart,
            pause=self.btnPause,
            stop=self.btnStop,
            emergency_reset=self.btnEmergencyReset,
        )
        self.control_buttons.setup()

        self._configure_hand_screen()
        self._configure_calibration_screen()
        self._configure_status_bar()
        self._connect_signals()

    # ------------------------------------------------------------------
    # Настройка меню и основных разделов
    # ------------------------------------------------------------------
    def _setup_menu(self) -> None:
        """Создать пункты меню и подключить обработчики."""

        self.menuAbout.triggered.connect(self.show_about_dialog)
        self.action_connection_settings = self.menu.addAction(
            "Параметры соединения..."
        )
        self.action_connection_settings.triggered.connect(
            self.show_connection_settings_dialog
        )
        self.action_graph_settings = self.menu.addAction("Настройки графиков")
        self.action_graph_settings.triggered.connect(
            self.show_graph_settings_dialog
        )
        self.action_general_settings = self.menu.addAction("Общие настройки")
        self.action_general_settings.triggered.connect(
            self.show_general_settings_dialog
        )

    def _configure_hand_screen(self) -> None:
        """Настроить виджеты и графики на экране ручного управления."""

        self.pageHand_pnlRight.config(
            model=self.model,
            led_dashboards=dashboards.hand_right_panel_led_dashboards,
        )

        default_graphs_cfg = dashboards.hand_graphs_setting_default
        graphs_cfg = self.config.cfg.get("graphs", {})
        for name, desc in dashboards.hand_graphs:
            cfg = graphs_cfg.get(name, {})
            desc["line_color"] = cfg.get("line_color", desc["line_color"])
            desc["background"] = cfg.get("background", desc["background"])
            desc["grid_color"] = cfg.get("grid_color", desc["grid_color"])
            desc["line_width"] = cfg.get("line_width", desc["line_width"])

        self.pageHand_pnlGraph.graph_config(
            model=self.model,
            plots_description=dashboards.hand_graphs,
        )
        self.pageHand_pnlTopDashboard.config(model=self.model)

    def _configure_calibration_screen(self) -> None:
        pass
        # подсказки IDE для self: Ui_MainWindow
        # self: "Ui_MainWindow" = cast("Ui_MainWindow", self)
        #
        # headers = ["Задание момента", "Значение", "Эталон"]
        # data = [
        #     [0.0, "", ""],
        #     [5.0, "", ""],
        #     [10.0, "", ""],
        #     [15.0, "", ""],
        #     [20.0, "", ""],
        #     [25.0, "", ""],
        #     [30.0, "", ""],
        #     [35.0, "", ""],
        #     [40.0, "", ""],
        #     [45.0, "", ""],
        #     [50.0, "", ""],
        # ]
        # new_table = self.make_table(headers, data)
        # new_table.setObjectName(u"table_calibrate_points")
        # lay = self.table_calibrate_points.parentWidget().layout()
        # lay.replaceWidget(self.table_calibrate_points, new_table)

    def _configure_status_bar(self) -> None:
        """Добавить виджет состояния соединения в строку состояния."""

        self.statusbar.addWidget(self.connection_ctrl)
        self.model.realtime_data.poller.connection_status.connect(
            self.connection_ctrl.set_status
        )

    def _connect_signals(self) -> None:
        """Подключить сигналы интерфейса к обработчикам."""

        self.btnHand.clicked.connect(self.on_btn_hand_click)
        self.btnInit.clicked.connect(self.on_btn_init_click)
        self.btnStatic1.clicked.connect(self.on_btn_static1_click)
        self.btnStatic2.clicked.connect(self.on_btn_static2_click)
        self.btnCalibration.clicked.connect(self.on_btn_calibration_click)
        self.btnProtocol.clicked.connect(self.on_btn_protocol_click)
        self.btnArchive.clicked.connect(self.on_btn_archive_click)
        self.btnService.clicked.connect(self.on_btn_service_click)

        self.btnInitNewTest.clicked.connect(self.on_btn_init_new_test_clicked)
        self.btnInitEdit.clicked.connect(self.on_btn_init_edit_clicked)
        self.btnInitSave.clicked.connect(self.on_btn_init_save_clicked)

        self.btnStart.clicked.connect(self.on_btn_start_clicked)
        self.btnPause.clicked.connect(self.on_btn_pause_clicked)
        self.btnStop.clicked.connect(self.on_btn_stop_clicked)
        self.btnEmergencyReset.clicked.connect(self.on_btn_emergency_reset_clicked)

        self.btnJog_CW.pressed.connect(self.on_jog_cw_pressed)
        self.btnJog_CCW.pressed.connect(self.on_jog_ccw_pressed)
        self.btnJog_CW.released.connect(self.on_jog_released)
        self.btnJog_CCW.released.connect(self.on_jog_released)
        self.btnHandRegSettings.clicked.connect(
            self.on_hand_reg_settings_clicked
        )

    # ------------------------------------------------------------------
    # Диалоги
    # ------------------------------------------------------------------
    @Slot()
    def show_about_dialog(self) -> None:
        """Отобразить диалог «О программе»."""

        AboutDialog(self).exec()

    @Slot()
    def show_connection_settings_dialog(self) -> None:
        """Показать диалог настроек соединения и применить изменения."""

        dlg = ConnectionSettingsDialog(self, config=self.config)
        if dlg.exec():
            dlg.apply_to_config(self.config)
            self.model.realtime_data.update_connection_settings()
            self.config.save()

    @Slot()
    def show_graph_settings_dialog(self) -> None:
        """Показать диалог изменения параметров отображения графиков."""

        dlg = GraphSettingsDialog(
            self,
            config=self.config,
            plots_description=dashboards.hand_graphs,
            graph_widgets=self.pageHand_pnlGraph.plots,
        )
        dlg.exec()

    @Slot()
    def show_general_settings_dialog(self) -> None:
        """Показать диалог общих настроек системы."""

        GeneralSettingsDialog(self, config=self.config).exec()

    # ------------------------------------------------------------------
    # Обработчики экранов
    # ------------------------------------------------------------------
    @Slot()
    def on_btn_hand_click(self) -> None:
        """Переключиться в режим ручного управления."""

        self.pager.setCurrentIndex(0)
        self.command_handler.set_plc_mode("hand")
        self.command_handler.servo_power_off()

    @Slot()
    def on_btn_init_click(self) -> None:
        """Перейти на экран инициализации и включить сервопривод."""

        self.pager.setCurrentIndex(1)
        self.command_handler.set_plc_mode("auto")
        self.command_handler.servo_power_on()

    @Slot()
    def on_btn_init_new_test_clicked(self) -> None:
        """Подготовить интерфейс к созданию записи нового испытания."""

        # Заглушка обработчика кнопки создания нового испытания.
        pass

    @Slot()
    def on_btn_init_edit_clicked(self) -> None:
        """Включить редактирование текущего набора данных испытания."""

        # Заглушка обработчика кнопки редактирования данных испытания.
        pass

    @Slot()
    def on_btn_init_save_clicked(self) -> None:
        """Сохранить введённые данные инициализации испытания."""

        # Заглушка обработчика кнопки сохранения данных испытания.
        pass

    @Slot()
    def on_btn_static1_click(self) -> None:
        """Перейти на экран первого статического теста."""

        self.pager.setCurrentIndex(2)
        self.command_handler.set_plc_mode("auto")
        self.command_handler.set_tension(222, 333)

    @Slot()
    def on_btn_static2_click(self) -> None:
        """Перейти на экран второго статического теста."""

        self.pager.setCurrentIndex(3)
        self.command_handler.set_plc_mode("auto")
        self.command_handler.set_tension(0, 0)

    @Slot()
    def on_btn_service_click(self) -> None:
        """Перейти на экран сервисного режима."""

        self.pager.setCurrentIndex(7)
        self.command_handler.set_plc_mode("service")

    @Slot()
    def on_btn_calibration_click(self) -> None:
        """Открыть экран калибровки датчиков."""

        self.pager.setCurrentIndex(4)

    @Slot()
    def on_btn_protocol_click(self) -> None:
        """Открыть экран протокола и результатов."""

        self.pager.setCurrentIndex(5)

    @Slot()
    def on_btn_archive_click(self) -> None:
        """Открыть экран архива."""

        self.pager.setCurrentIndex(6)

    # ------------------------------------------------------------------
    # Кнопки управления испытанием
    # ------------------------------------------------------------------
    @Slot(bool)
    def on_btn_start_clicked(self, checked: bool) -> None:
        """Обработать нажатие кнопки запуска."""

        if not checked:
            self.control_buttons.ensure_start_checked()
            return
        self.control_buttons.enable_pause()
        self.handle_start_command()

    @Slot(bool)
    def on_btn_pause_clicked(self, checked: bool) -> None:
        """Обработать нажатие кнопки паузы."""

        if not self.btnStart.isChecked():
            self.control_buttons.disable_pause()
            return
        self.handle_pause_command(checked)

    @Slot()
    def on_btn_stop_clicked(self) -> None:
        """Обработать нажатие кнопки стоп."""

        self.control_buttons.reset()
        self.handle_stop_command()

    @Slot()
    def on_btn_emergency_reset_clicked(self) -> None:
        """Обработать нажатие кнопки сброса аварии."""

        self.handle_emergency_reset_command()

    # ------------------------------------------------------------------
    # Ручное управление приводом
    # ------------------------------------------------------------------
    def on_jog_cw_pressed(self) -> None:
        """Поворот по часовой стрелке, пока кнопка нажата."""

        self.model.command_handler.jog(direction="cw", velocity=0)
        logger.info("cw")

    def on_jog_ccw_pressed(self) -> None:
        """Поворот против часовой стрелки, пока кнопка нажата."""

        self.model.command_handler.jog(direction="ccw", velocity=0)
        logger.info("ccw")

    def on_jog_released(self) -> None:
        """Остановить поворот при отпускании кнопки."""

        self.model.command_handler.stop()
        logger.info("stop")

    def on_hand_reg_settings_clicked(self) -> None:
        """Открыть диалог настроек ручного регулятора."""

        HandRegulatorSettingsDialog(self).exec()

    # ------------------------------------------------------------------
    # Заглушки для команд управления
    # ------------------------------------------------------------------
    def handle_start_command(self) -> None:
        """Заглушка обработчика команды запуска."""

        pass

    def handle_pause_command(self, is_paused: bool) -> None:
        """Заглушка обработчика команды паузы или продолжения."""

        del is_paused
        pass

    def handle_stop_command(self) -> None:
        """Заглушка обработчика команды остановки."""

        pass

    def handle_emergency_reset_command(self) -> None:
        """Заглушка обработчика команды сброса аварии."""

        pass

    # ===========================================
    # Вспомогательные функции работы с таблицами
    # ===========================================
    def make_table(self, headers: List[str], rows: Iterable[Iterable[object]]) -> QTableWidget:
        table = QTableWidget()
        table.setColumnCount(len(headers))
        table.setHorizontalHeaderLabels(headers)

        # Базовые настройки UX
        #table.setAlternatingRowColors(True)
        table.setSortingEnabled(False)
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
        self.resize_to_contents(table)
        self.center_column(table, 0)
        return table

    # Ресайз таблицы по содержимому
    def resize_to_contents(self, table: QTableWidget) -> None:
        header = table.horizontalHeader()
        header.setSectionResizeMode(QHeaderView.ResizeMode.ResizeToContents)
        # Немного увеличить последнюю колонку, чтобы не было прижатия
        header.setStretchLastSection(True)

    # Выравнивание n-ого столбца таблицы по центру
    def center_column(self, table: QTableWidget, col: int):
        for r in range(table.rowCount()):
            it = table.item(r, col)
            if it is None:
                it = QTableWidgetItem("")
                table.setItem(r, col, it)
            it.setTextAlignment(Qt.AlignmentFlag.AlignHCenter | Qt.AlignmentFlag.AlignVCenter)