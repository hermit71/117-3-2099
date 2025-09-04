from PyQt6.QtWidgets import (
    QMainWindow, QWidget, QHBoxLayout, QVBoxLayout, QPushButton, QStackedWidget,
    QMenuBar, QStatusBar, QDialog, QFormLayout, QLineEdit, QDialogButtonBox, QLabel
)
from PyQt6.QtCore import pyqtSlot as Slot
from src.ui.main_117_3 import Ui_MainWindow
from src.ui.dlgPID_settings import Ui_dlgHandRegulatorSettings
from src.data.model import Model
from src.ui.widgets import dashboards, connection_control_widget as cw


class ConnectionSettingsDialog(QDialog):
    def __init__(self, parent=None, config=None):
        super().__init__(parent)
        self.setWindowTitle("Параметры соединения")
        self.config = config

        form = QFormLayout(self)

        self.ed_host = QLineEdit(self.config.get('modbus', 'host', '127.0.0.1'))
        self.ed_port = QLineEdit(str(self.config.get('modbus', 'port', 502)))
        self.ed_timeout = QLineEdit(str(self.config.get('modbus', 'timeout', 2.0)))
        self.ed_poll = QLineEdit(str(self.config.get('ui', 'poll_interval_ms', 200)))

        form.addRow("IP-адрес ПЛК:", self.ed_host)
        form.addRow("Порт:", self.ed_port)
        form.addRow("Таймаут (с):", self.ed_timeout)
        form.addRow("Период опроса (мс):", self.ed_poll)

        buttons = QDialogButtonBox(QDialogButtonBox.StandardButton.Ok | QDialogButtonBox.StandardButton.Cancel)
        form.addRow(buttons)
        buttons.accepted.connect(self.accept)
        buttons.rejected.connect(self.reject)

    def accept(self):
        # Валидация данных можно добавить здесь
        super().accept()


class AboutDialog(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("О программе")
        v = QVBoxLayout(self)
        v.addWidget(QLabel("Шаблон интерфейса стенда крутильных статических испытаний. PyQt6 + pyqtgraph + Modbus TCP."))


class MainWindow(QMainWindow, Ui_MainWindow):
    def __init__(self, config):
        super().__init__()
        self.config = config
        self.setupUi(self)
        self.model = Model()
        self.command_handler = self.model.command_handler
        self.connection_ctrl = cw.connectionControl()
        self.hand_screen_config()
        self.statusbar_config()
        self.signal_connections()

    def signal_connections(self):
        self.btnHand.clicked.connect(self.on_btnHand_click)
        self.btnInit.clicked.connect(self.on_btnInit_click)
        self.btnStatic1.clicked.connect(self.on_btnStatic1_click)
        self.btnStatic2.clicked.connect(self.on_btnStatic2_click)
        self.btnService.clicked.connect(self.on_btnService_click)

        self.btnJog_CW.pressed.connect(self.on_jog_cw_pressed)
        self.btnJog_CCW.pressed.connect(self.on_jog_ccw_pressed)
        self.btnJog_CW.released.connect(self.on_jog_released)
        self.btnJog_CCW.released.connect(self.on_jog_released)
        self.btnHandRegSettings.clicked.connect(self.on_hand_reg_settings_clicked)

    @Slot()
    def on_btnHand_click(self):
        self.pager.setCurrentIndex(0)
        self.command_handler.set_plc_mode('hand')
        self.command_handler.servo_power_off()

    @Slot()
    def on_btnInit_click(self):
        self.pager.setCurrentIndex(1)
        self.command_handler.set_plc_mode('auto')
        self.command_handler.servo_power_on()

    @Slot()
    def on_btnStatic1_click(self):
        self.pager.setCurrentIndex(2)
        self.command_handler.set_plc_mode('auto')
        self.command_handler.set_tension(222,333)

    @Slot()
    def on_btnStatic2_click(self):
        self.pager.setCurrentIndex(3)
        self.command_handler.set_plc_mode('auto')
        self.command_handler.set_tension(0,0)

    @Slot()
    def on_btnService_click(self):
        self.pager.setCurrentIndex(4)
        self.command_handler.set_plc_mode('service')

    def on_jog_cw_pressed(self):
        self.model.command_handler.jog(direction='cw', velocity=0)
        print('cw')

    def on_jog_ccw_pressed(self):
        self.model.command_handler.jog(direction='ccw', velocity=0)
        print('ccw')

    def on_jog_released(self):
        self.model.command_handler.stop()
        print('stop')

    def on_hand_reg_settings_clicked(self):
        dlg = QDialog()
        ui = Ui_dlgHandRegulatorSettings()
        ui.setupUi(dlg)
        dlg.exec()

    def hand_screen_config(self):
        # Конфигурация правой индикаторной панели
        self.pageHand_pnlRight.config(model=self.model, led_dashboards=dashboards.hand_right_panel_led_dashboards)
        # Конфигурация графиков
        self.pageHand_pnlGraph.graph_config(model=self.model, plots_description=dashboards.hand_graphs)
        # Конфигурация дашборда (показания датчиков)
        self.pageHand_pnlTopDashboard.config(model=self.model)

    def statusbar_config(self):
        self.statusbar.addWidget(self.connection_ctrl)
        self.model.realtime_data.worker.connection_status.connect(self.connection_ctrl.setStatus)