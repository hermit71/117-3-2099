from PyQt6.QtWidgets import (
    QMainWindow,
    QDialog,
    QMessageBox,
)

from PyQt6.QtCore import pyqtSlot as Slot
from PyQt6.QtGui import QIntValidator
import ipaddress
import logging
from src.ui.main_117_3_ui import Ui_MainWindow
from src.ui.dlgPID_settings_ui import Ui_dlgHandRegulatorSettings
from src.ui.about_dialog_ui import Ui_AboutDialog
from src.ui.connection_settings_dialog_ui import Ui_ConnectionSettingsDialog
from src.ui.graph_settings_dialog import GraphSettingsDialog
from src.ui.general_settings_dialog import GeneralSettingsDialog
from src.data.model import Model
from src.ui.widgets import dashboards, connection_control_widget as cw

logger = logging.getLogger(__name__)


class ConnectionSettingsDialog(QDialog, Ui_ConnectionSettingsDialog):
    """Dialog window for editing Modbus connection parameters.

    Диалоговое окно для редактирования параметров соединения Modbus.
    """

    def __init__(self, parent=None, config=None):
        super().__init__(parent)
        self.config = config
        self.setupUi(self)
        self.ed_host.setText(self.config.get("modbus", "host", "127.0.0.1"))
        self.ed_port.setText(str(self.config.get("modbus", "port", 502)))
        self.ed_timeout.setText(str(self.config.get("modbus", "timeout", 2.0)))
        self.ed_poll.setText(str(self.config.get("ui", "poll_interval_ms", 200)))
        self.ed_port.setValidator(QIntValidator(1, 65535, self))

    def accept(self):
        """Validate and accept the dialog.

        Проверить и применить данные диалога.
        """
        host = self.ed_host.text().strip()
        port_text = self.ed_port.text().strip()
        try:
            ipaddress.ip_address(host)
        except ValueError:
            QMessageBox.warning(
                self,
                "Неверный IP",
                "Введите IP-адрес в формате 192.168.0.1",
            )
            return

        if not port_text.isdigit():
            QMessageBox.warning(
                self,
                "Неверный порт",
                "Введите порт в диапазоне 1-65535, например, 502",
            )
            return

        port = int(port_text)
        if not (1 <= port <= 65535):
            QMessageBox.warning(
                self,
                "Неверный порт",
                "Введите порт в диапазоне 1-65535, например, 502",
            )
            return

        super().accept()


class AboutDialog(QDialog, Ui_AboutDialog):
    """Dialog displaying information about the application.

    Диалог, отображающий информацию о приложении.
    """

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setupUi(self)


class MainWindow(QMainWindow, Ui_MainWindow):
    """Main application window coordinating UI components and actions.

    Главное окно приложения, координирующее компоненты интерфейса и действия.
    """

    def __init__(self, config):
        super().__init__()
        self.config = config
        self.setupUi(self)
        self.menuAbout.triggered.connect(self.show_about_dialog)
        # Настройки соединения Modbus
        self.actionConnectionSettings = self.menu.addAction(
            "Параметры соединения..."
        )
        self.actionConnectionSettings.triggered.connect(
            self.show_connection_settings_dialog
        )
        # Настройки графиков
        self.actionGraphSettings = self.menu.addAction("Настройки графиков")
        self.actionGraphSettings.triggered.connect(
            self.show_graph_settings_dialog
        )
        # Общие настройки системы
        self.actionGeneralSettings = self.menu.addAction("Общие настройки")
        self.actionGeneralSettings.triggered.connect(
            self.show_general_settings_dialog
        )
        self.model = Model(self.config)
        self.command_handler = self.model.command_handler
        self.connection_ctrl = cw.ConnectionControl()
        self.hand_screen_config()
        self.statusbar_config()
        self.control_buttons_config()
        self.signal_connections()
        # self.btnHand.setStyleSheet(
        #     """
        #     QPushButton {
        #         background-color: #3498db;
        #         color: white;
        #         border-radius: 5px;
        #         padding: 5px 10px;
        #     }
        #     QPushButton:hover {
        #         background-color: #2980b9;
        #     }
        # """
        # )

    def signal_connections(self):
        """Connect UI signals to their respective handlers.

        Подключить сигналы интерфейса к соответствующим обработчикам.
        """
        self.btnHand.clicked.connect(self.on_btn_hand_click)
        self.btnInit.clicked.connect(self.on_btn_init_click)
        self.btnStatic1.clicked.connect(self.on_btn_static1_click)
        self.btnStatic2.clicked.connect(self.on_btn_static2_click)
        self.btnCalibration.clicked.connect(self.on_btn_calibration_click)
        self.btnProtocol.clicked.connect(self.on_btn_protocol_click)
        self.btnArchive.clicked.connect(self.on_btn_archive_click)
        self.btnService.clicked.connect(self.on_btn_service_click)

        self.btnStart.clicked.connect(self.on_btn_start_clicked)
        self.btnPause.clicked.connect(self.on_btn_pause_clicked)
        self.btnStop.clicked.connect(self.on_btn_stop_clicked)
        self.btnEmergencyReset.clicked.connect(
            self.on_btn_emergency_reset_clicked
        )

        self.btnJog_CW.pressed.connect(self.on_jog_cw_pressed)
        self.btnJog_CCW.pressed.connect(self.on_jog_ccw_pressed)
        self.btnJog_CW.released.connect(self.on_jog_released)
        self.btnJog_CCW.released.connect(self.on_jog_released)
        self.btnHandRegSettings.clicked.connect(self.on_hand_reg_settings_clicked)

    @Slot()
    def show_about_dialog(self):
        """Display the About dialog.

        Отобразить диалог «О программе».
        """
        dlg = AboutDialog(self)
        dlg.exec()

    @Slot()
    def show_connection_settings_dialog(self):
        """Display and apply connection settings dialog.

        Показать диалог настроек соединения и применить изменения.
        """
        dlg = ConnectionSettingsDialog(self, config=self.config)
        if dlg.exec():
            self.config.cfg.setdefault("modbus", {})
            self.config.cfg.setdefault("ui", {})
            self.config.cfg["modbus"]["host"] = dlg.ed_host.text()
            self.config.cfg["modbus"]["port"] = int(dlg.ed_port.text())
            self.config.cfg["modbus"]["timeout"] = float(
                dlg.ed_timeout.text()
            )
            self.config.cfg["ui"]["poll_interval_ms"] = int(
                dlg.ed_poll.text()
            )
            self.model.realtime_data.update_connection_settings()
            self.config.save()

    @Slot()
    def show_graph_settings_dialog(self):
        """Display dialog to edit graph appearance settings.

        Показать диалог изменения параметров отображения графиков.
        """
        dlg = GraphSettingsDialog(
            self,
            config=self.config,
            plots_description=dashboards.hand_graphs,
            graph_widgets=self.pageHand_pnlGraph.plots,
        )
        dlg.exec()

    @Slot()
    def show_general_settings_dialog(self):
        """Display dialog for general system settings.

        Показать диалог общих настроек системы.
        """
        dlg = GeneralSettingsDialog(self, config=self.config)
        dlg.exec()

    @Slot()
    def on_btn_hand_click(self):
        """Switch to manual control mode.

        Переключиться в режим ручного управления.
        """
        self.pager.setCurrentIndex(0)
        self.command_handler.set_plc_mode("hand")
        self.command_handler.servo_power_off()

    @Slot()
    def on_btn_init_click(self):
        """Switch to initialization screen and enable servo.

        Перейти на экран инициализации и включить сервопривод.
        """
        self.pager.setCurrentIndex(1)
        self.command_handler.set_plc_mode("auto")
        self.command_handler.servo_power_on()

    @Slot()
    def on_btn_static1_click(self):
        """Switch to first static test screen.

        Перейти на экран первого статического теста.
        """
        self.pager.setCurrentIndex(2)
        self.command_handler.set_plc_mode("auto")
        self.command_handler.set_tension(222, 333)

    @Slot()
    def on_btn_static2_click(self):
        """Switch to second static test screen.

        Перейти на экран второго статического теста.
        """
        self.pager.setCurrentIndex(3)
        self.command_handler.set_plc_mode("auto")
        self.command_handler.set_tension(0, 0)

    @Slot()
    def on_btn_service_click(self):
        """Switch to service mode screen.

        Перейти на экран сервисного режима.
        """
        self.pager.setCurrentIndex(7)
        self.command_handler.set_plc_mode("service")

    @Slot()
    def on_btn_calibration_click(self):
        """Open sensors calibration screen.

        Открыть экран калибровки датчиков.
        """
        self.pager.setCurrentIndex(4)

    @Slot()
    def on_btn_protocol_click(self):
        """Open protocol and results screen.

        Открыть экран протокола и результатов.
        """
        self.pager.setCurrentIndex(5)

    @Slot()
    def on_btn_archive_click(self):
        """Open archive screen.

        Открыть экран архива.
        """
        self.pager.setCurrentIndex(6)

    @Slot(bool)
    def on_btn_start_clicked(self, checked):
        """Handle start button clicks and manage control buttons state.

        Обработать нажатие кнопки запуска и управлять состоянием кнопок
        управления.
        """

        if not checked:
            self.btnStart.blockSignals(True)
            self.btnStart.setChecked(True)
            self.btnStart.blockSignals(False)
            return

        self.btnPause.setEnabled(True)
        self.btnPause.blockSignals(True)
        self.btnPause.setChecked(False)
        self.btnPause.blockSignals(False)
        self.handle_start_command()

    @Slot(bool)
    def on_btn_pause_clicked(self, checked):
        """Handle pause button clicks when start is active.

        Обработать нажатия кнопки паузы, когда активен режим запуска.
        """

        if not self.btnStart.isChecked():
            self.btnPause.blockSignals(True)
            self.btnPause.setChecked(False)
            self.btnPause.blockSignals(False)
            self.btnPause.setEnabled(False)
            return

        self.handle_pause_command(checked)

    @Slot()
    def on_btn_stop_clicked(self):
        """Handle stop button clicks and reset button states.

        Обработать нажатие кнопки стоп и вернуть кнопки в исходное
        состояние.
        """

        self.reset_control_buttons_state()
        self.handle_stop_command()

    @Slot()
    def on_btn_emergency_reset_clicked(self):
        """Handle emergency reset button clicks.

        Обработать нажатие кнопки сброса аварии.
        """

        self.handle_emergency_reset_command()

    def on_jog_cw_pressed(self):
        """Jog clockwise while button is pressed.

        Поворот по часовой стрелке, пока кнопка нажата.
        """
        self.model.command_handler.jog(direction="cw", velocity=0)
        logger.info("cw")

    def on_jog_ccw_pressed(self):
        """Jog counter-clockwise while button is pressed.

        Поворот против часовой стрелки, пока кнопка нажата.
        """
        self.model.command_handler.jog(direction="ccw", velocity=0)
        logger.info("ccw")

    def on_jog_released(self):
        """Stop jogging when button is released.

        Остановить поворот при отпускании кнопки.
        """
        self.model.command_handler.stop()
        logger.info("stop")

    def on_hand_reg_settings_clicked(self):
        """Open dialog for hand regulator settings.

        Открыть диалог настроек ручного регулятора.
        """
        dlg = QDialog()
        ui = Ui_dlgHandRegulatorSettings()
        ui.setupUi(dlg)
        dlg.exec()

    def hand_screen_config(self):
        """Configure widgets and graphs for the hand control screen.

        Настроить виджеты и графики для экрана ручного управления.
        """
        # Конфигурация правой индикаторной панели
        self.pageHand_pnlRight.config(
            model=self.model, led_dashboards=dashboards.hand_right_panel_led_dashboards
        )
        # Конфигурация графиков
        graphs_cfg = self.config.cfg.get("graphs", {})
        for name, desc in dashboards.hand_graphs:
            cfg = graphs_cfg.get(name, {})
            desc["line_color"] = cfg.get("line_color", desc["line_color"])
            desc["background"] = cfg.get("background", desc["background"])
            desc["grid_color"] = cfg.get("grid_color", desc["grid_color"])
            desc["line_width"] = cfg.get("line_width", desc["line_width"])
        self.pageHand_pnlGraph.graph_config(
            model=self.model, plots_description=dashboards.hand_graphs
        )
        # Конфигурация дашборда (показания датчиков)
        self.pageHand_pnlTopDashboard.config(model=self.model)

    def statusbar_config(self):
        """Add the connection control widget to the status bar.

        Добавить виджет управления соединением на строку состояния.
        """
        self.statusbar.addWidget(self.connection_ctrl)
        self.model.realtime_data.worker.connection_status.connect(
            self.connection_ctrl.set_status
        )

    def control_buttons_config(self):
        """Configure control buttons appearance and default state.

        Настроить внешний вид и исходное состояние кнопок управления
        испытанием.
        """

        self.btnStart.setCheckable(True)
        self.btnPause.setCheckable(True)
        self.btnPause.setEnabled(False)

        self.btnStart.setStyleSheet(
            """
            QPushButton:checked {
                background-color: #4caf50;
                color: white;
            }
            """
        )
        self.btnPause.setStyleSheet(
            """
            QPushButton:checked {
                background-color: #f9f2a8;
                color: black;
            }
            """
        )

    def reset_control_buttons_state(self):
        """Return control buttons to their default state.

        Вернуть кнопки управления в исходное состояние.
        """

        self.btnStart.blockSignals(True)
        self.btnPause.blockSignals(True)
        self.btnStart.setChecked(False)
        self.btnPause.setChecked(False)
        self.btnStart.blockSignals(False)
        self.btnPause.blockSignals(False)
        self.btnPause.setEnabled(False)

    def handle_start_command(self):
        """Placeholder for start command handling.

        Заглушка обработчика команды запуска.
        """

        pass

    def handle_pause_command(self, is_paused: bool):
        """Placeholder for pause/resume command handling.

        Заглушка обработчика команды паузы или продолжения.

        :param is_paused: Текущее состояние кнопки паузы.
        """

        del is_paused
        pass

    def handle_stop_command(self):
        """Placeholder for stop command handling.

        Заглушка обработчика команды остановки.
        """

        pass

    def handle_emergency_reset_command(self):
        """Placeholder for emergency reset command handling.

        Заглушка обработчика команды сброса аварии.
        """

        pass

