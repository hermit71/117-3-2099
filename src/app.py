import sys
from PyQt6.QtWidgets import QApplication, QMainWindow, QDialog
from PyQt6.QtCore import pyqtSlot as Slot
from src.ui.main_117_3 import Ui_MainWindow
from src.ui.dlgPID_settings import Ui_dlgHandRegulatorSettings
from src.data.model import Model
from src.ui.widgets import dashboards, connection_control_widget as cw


class MainWindow_117_3(QMainWindow, Ui_MainWindow):
    def __init__(self, *args, obj=None, **kwargs):
        super().__init__(*args, **kwargs)
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

# class MainWindow(QMainWindow, Ui_MainWindow):
#
#     def __init__(self, *args, obj=None, **kwargs):
#         super().__init__(*args, **kwargs)
#         setting = Setting()
#
#         # Контейнер для данных, полученных во время испытаний или в реальном времени от датчиков стенда
#         self.model = Model()
#
#         self.setupUi(self)
#         self.setup_right_panel()
#         print('From MainWindow: ', self.model)
#         self.main_right_panel = MainRightPanel(self, model=self.model)
#
#         self.timer = QTimer()
#         self.timer.timeout.connect(self.on_timer) # type: ignore
#         self.timer.start(100)
#
#         # Настройка графика
#         pen = pg.mkPen(color="#1C1CF0", width=2)
#
#         self.graph_window = 2000 # Количество точек для отображения на графике
#
#         #self.graph_tension.setBackground('w')
#         self.graph_tension.setLabel('left', 'Крутящий момент', 'Нм')
#         self.graph_tension.setLabel('bottom', 'Время', 'мс')
#         self.graph_tension.showGrid(x=True, y=True)
#         self.curve_tension = self.graph_tension.plot(pen=pen)
#
#         #self.graph_angle.setBackground('w')
#         self.graph_angle.setLabel('left', 'Угол поворота', '\u00B0')
#         self.graph_angle.setLabel('bottom', 'Время', 'мс')
#         self.graph_angle.showGrid(x=True, y=True)
#         self.curve_angle = self.graph_angle.plot(pen=pen)
#
#         #self.graph_velocity.setBackground('w')
#         self.graph_velocity.setLabel('left', 'Скорость изменения М', 'Н/с')
#         self.graph_velocity.setLabel('bottom', 'Время', 'мс')
#         self.graph_velocity.showGrid(x=True, y=True)
#         self.curve_velocity = self.graph_velocity.plot(pen=pen)
#
#         # Синхронизация осей X графиков
#         self.graph_tension.setXLink(self.graph_angle)  # Связываем ось X второго графика с первым
#         self.graph_angle.setXLink(self.graph_velocity)
#
#         self.signal_connection()
#
#     def signal_connection(self):
#         self.btnHand.clicked.connect(self.on_btnHand_click)
#
#         self.btnInit.clicked.connect(self.on_btnInit_click)
#
#         self.btnStatic1.clicked.connect(self.on_btnStatic1_click)
#
#         self.btnStatic2.clicked.connect(self.on_btnStatic2_click)
#
#         self.btnService.clicked.connect(self.on_btnService_click)
#
#     def setup_right_panel(self):
#         self.right_led_alarm_status = LedPanel(
#             title='Контроль цепей безопасности',
#             labels=lbl.alarm_led_labels)
#         self.right_led_ups_status = LedPanel(
#             led_number=3, title='Контроль состояния ИБП',
#             labels=lbl.ups_led_labels)
#         self.right_led_alarm_status.set_led_color(4, app_colors['red'], app_colors['grey_red'])
#         self.right_led_alarm_status.set_led_color(5, app_colors['red'], app_colors['grey_red'])
#         self.right_led_alarm_status.set_led_color(6, app_colors['red'], app_colors['grey_red'])
#         self.right_led_ups_status.set_led_color(1, app_colors['red'], app_colors['grey_red'])
#         self.right_led_ups_status.set_led_color(2, app_colors['red'], app_colors['grey_red'])
#         self.spacer_001 = QSpacerItem(20, 40, QSizePolicy.Policy.Minimum, QSizePolicy.Policy.Expanding)
#         self.vBox_r_panel.addWidget(self.right_led_alarm_status)
#         self.vBox_r_panel.addWidget(self.right_led_ups_status)
#         self.vBox_r_panel.addSpacerItem(self.spacer_001)
#
#     @Slot()
#     def on_btnHand_click(self):
#         self.mainStack.setCurrentIndex(0)
#         self.model.set_plc_mode('hand')
#
#     @Slot()
#     def on_btnInit_click(self):
#         self.mainStack.setCurrentIndex(1)
#         self.model.set_plc_mode('auto')
#
#     @Slot()
#     def on_btnStatic1_click(self):
#         self.mainStack.setCurrentIndex(2)
#         self.model.set_plc_mode('auto')
#
#     @Slot()
#     def on_btnStatic2_click(self):
#         self.mainStack.setCurrentIndex(3)
#         self.model.set_plc_mode('auto')
#
#     @Slot()
#     def on_btnService_click(self):
#         self.mainStack.setCurrentIndex(4)
#         self.model.set_plc_mode('service')
#
#     @Slot()
#     def on_btnStartPoll_click(self):
#         pass
#
#     @Slot()
#     def on_timer(self):
#         display_points = 2000
#         start_idx = max(0, self.model.realtime_data.ptr - display_points)
#         time_data = self.model.realtime_data.times[:self.model.realtime_data.ptr]
#         value_data = self.model.realtime_data.tension_data[:self.model.realtime_data.ptr]
#         if time_data.size > 0:
#             vectorized_adc_convert = np.vectorize(adc_convert)
#             value_data_converted = vectorized_adc_convert(value_data)
#             self.curve_tension.setData(time_data, value_data_converted)
#             tension_Nm = value_data_converted[-1]
#             angle_deg = float(self.model.realtime_data.angle_data[0]) / 728.0
#             self.leTension.setText(f'{tension_Nm:.2f} Нм')
#             self.leTension.setAlignment(Qt.AlignmentFlag.AlignCenter)
#             self.leAngle.setText(f'{angle_deg:.1f} \u00B0')
#             self.leAngle.setAlignment(Qt.AlignmentFlag.AlignCenter)
#             self.leVelocity.setText(f'{0:.1f} Н/с')
#
#         self.graph_tension.setXRange(start_idx, start_idx + display_points)
#         self.graph_angle.setXRange(start_idx, start_idx + display_points)
#         self.graph_velocity.setXRange(start_idx, start_idx + display_points)
#
#         self.right_led_alarm_status.set_status(self.model.realtime_data.in_status)
#         self.right_led_ups_status.set_status(self.model.realtime_data.ups_status)



def adc_convert(idc_value):
    return 100 * float(idc_value) / 32768.0

if __name__ == '__main__':
    app = QApplication(sys.argv)
    app.setStyle('Fusion')
    window = MainWindow_117_3()
    window.setGeometry(700, 50, 500, 400)
    window.on_btnHand_click()
    window.show()
    #window.showMaximized()
    sys.exit(app.exec())