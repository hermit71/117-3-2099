from PyQt6.QtCore import QObject

class Setting(QObject):
    def __init__(self):
        super().__init__()
        self.PLC_IP = '192.168.6.31'
