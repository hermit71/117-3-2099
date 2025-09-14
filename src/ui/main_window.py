from PyQt6.QtWidgets import (
    QMainWindow,
    QVBoxLayout,
    QDialog,
    QFormLayout,
    QLineEdit,
    QDialogButtonBox,
    QLabel,
)
from PyQt6.QtCore import pyqtSlot as Slot
import logging
from src.ui.main_117_3 import Ui_MainWindow
from src.ui.dlgPID_settings import Ui_dlgHandRegulatorSettings
from src.ui.about_dialog import Ui_AboutDialog
from src.data.model import Model
from src.ui.widgets import dashboards, connection_control_widget as cw

logger = logging.getLogger(__name__)


class ConnectionSettingsDialog(QDialog):
    """Dialog window for editing Modbus connection parameters."""

    def __init__(self, parent=None, config=None):
        super().__init__(parent)
        self.setWindowTitle("Параметры соединения")
        self.config = config

        form = QFormLayout(self)

        self.ed_host = QLineEdit(self.config.get("modbus", "host", "127.0.0.1"))
        self.ed_port = QLineEdit(str(self.config.get("modbus", "port", 502)))
        self.ed_timeout = QLineEdit(str(self.config.get("modbus", "timeout", 2.0)))
        self.ed_poll = QLineEdit(str(self.config.get("ui", "poll_interval_ms", 200)))

        form.addRow("IP-адрес ПЛК:", self.ed_host)
        form.addRow("Порт:", self.ed_port)
        form.addRow("Таймаут (с):", self.ed_timeout)
        form.addRow("Период опроса (мс):", self.ed_poll)

        buttons = QDialogButtonBox(
            QDialogButtonBox.StandardButton.Ok | QDialogButtonBox.StandardButton.Cancel
        )
        form.addRow(buttons)
        buttons.accepted.connect(self.accept)
        buttons.rejected.connect(self.reject)

    def accept(self):
        """Validate and accept the dialog."""
        # Валидация данных можно добавить здесь
        super().accept()


class AboutDialog(QDialog, Ui_AboutDialog):
    """Dialog displaying information about the application."""

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setupUi(self)


class MainWindow(QMainWindow, Ui_MainWindow):
    """Main application window coordinating UI components and actions."""

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
        self.model = Model(self.config)
        self.command_handler = self.model.command_handler
        self.connection_ctrl = cw.ConnectionControl()
        self.hand_screen_config()
        self.statusbar_config()
        self.signal_connections()
        self.btnHand.setStyleSheet(
            """
            QPushButton {
                background-color: #3498db;
                color: white;
                border-radius: 5px;
                padding: 5px 10px;
            }
            QPushButton:hover {
                background-color: #2980b9;
            }
        """
        )

    def signal_connections(self):
        """Connect UI signals to their respective handlers."""
        self.btnHand.clicked.connect(self.on_btn_hand_click)
        self.btnInit.clicked.connect(self.on_btn_init_click)
        self.btnStatic1.clicked.connect(self.on_btn_static1_click)
        self.btnStatic2.clicked.connect(self.on_btn_static2_click)
        self.btnService.clicked.connect(self.on_btn_service_click)

        self.btnJog_CW.pressed.connect(self.on_jog_cw_pressed)
        self.btnJog_CCW.pressed.connect(self.on_jog_ccw_pressed)
        self.btnJog_CW.released.connect(self.on_jog_released)
        self.btnJog_CCW.released.connect(self.on_jog_released)
        self.btnHandRegSettings.clicked.connect(self.on_hand_reg_settings_clicked)

    @Slot()
    def show_about_dialog(self):
        """Display the About dialog."""
        dlg = AboutDialog(self)
        dlg.exec()

    @Slot()
    def show_connection_settings_dialog(self):
        """Display and apply connection settings dialog."""
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

    @Slot()
    def on_btn_hand_click(self):
        """Switch to manual control mode."""
        self.pager.setCurrentIndex(0)
        self.command_handler.set_plc_mode("hand")
        self.command_handler.servo_power_off()

    @Slot()
    def on_btn_init_click(self):
        """Switch to initialization screen and enable servo."""
        self.pager.setCurrentIndex(1)
        self.command_handler.set_plc_mode("auto")
        self.command_handler.servo_power_on()

    @Slot()
    def on_btn_static1_click(self):
        """Switch to first static test screen."""
        self.pager.setCurrentIndex(2)
        self.command_handler.set_plc_mode("auto")
        self.command_handler.set_tension(222, 333)

    @Slot()
    def on_btn_static2_click(self):
        """Switch to second static test screen."""
        self.pager.setCurrentIndex(3)
        self.command_handler.set_plc_mode("auto")
        self.command_handler.set_tension(0, 0)

    @Slot()
    def on_btn_service_click(self):
        """Switch to service mode screen."""
        self.pager.setCurrentIndex(4)
        self.command_handler.set_plc_mode("service")

    def on_jog_cw_pressed(self):
        """Jog clockwise while button is pressed."""
        self.model.command_handler.jog(direction="cw", velocity=0)
        logger.info("cw")

    def on_jog_ccw_pressed(self):
        """Jog counter-clockwise while button is pressed."""
        self.model.command_handler.jog(direction="ccw", velocity=0)
        logger.info("ccw")

    def on_jog_released(self):
        """Stop jogging when button is released."""
        self.model.command_handler.stop()
        logger.info("stop")

    def on_hand_reg_settings_clicked(self):
        """Open dialog for hand regulator settings."""
        dlg = QDialog()
        ui = Ui_dlgHandRegulatorSettings()
        ui.setupUi(dlg)
        dlg.exec()

    def hand_screen_config(self):
        """Configure widgets and graphs for the hand control screen."""
        # Конфигурация правой индикаторной панели
        self.pageHand_pnlRight.config(
            model=self.model, led_dashboards=dashboards.hand_right_panel_led_dashboards
        )
        # Конфигурация графиков
        self.pageHand_pnlGraph.graph_config(
            model=self.model, plots_description=dashboards.hand_graphs
        )
        # Конфигурация дашборда (показания датчиков)
        self.pageHand_pnlTopDashboard.config(model=self.model)

    def statusbar_config(self):
        """Add the connection control widget to the status bar."""
        self.statusbar.addWidget(self.connection_ctrl)
        self.model.realtime_data.worker.connection_status.connect(
            self.connection_ctrl.set_status
        )

