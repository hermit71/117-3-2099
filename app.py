import sys
from PyQt6.QtWidgets import QApplication, QMainWindow, QDialog
from src.ui.main_window import MainWindow
from src.utils.config import Config


def adc_convert(idc_value):
    return 100 * float(idc_value) / 32768.0

if __name__ == '__main__':
    app = QApplication(sys.argv)
    app.setStyle('Fusion')
    config = Config('config/config.yaml')
    window = MainWindow(config)
    window.setGeometry(250, 50, 900, 600)
    window.on_btnHand_click()
    window.show()
    #window.showMaximized()
    sys.exit(app.exec())



# todo: убрать скакание значений датчиков особенно при переходе от - к + !