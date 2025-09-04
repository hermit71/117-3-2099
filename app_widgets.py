from PyQt6.QtWidgets import QWidget
from led_panel import Ui_Form

class app_led_panel(QWidget, Ui_Form):
    def __init__(self, parent=None):
        super(app_led_panel, self).__init__(parent)
        self.setupUi(self)

        self.led_array = [self.led_1, self.led_2, self.led_3, self.led_4]
        self.led_array = list(map(lambda x: x.setEnabled(True), self.led_array))
        for i, l in enumerate(self.led_array):
            #l.setEnabled(True)
            print(f"{i}: {l.isEnabled()}")

