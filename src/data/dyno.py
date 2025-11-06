from PyQt6.QtCore import QObject, pyqtSignal, Qt
from PyQt6.QtSerialPort import QSerialPort, QSerialPortInfo
from PyQt6.QtWidgets import QApplication, QWidget, QVBoxLayout, QPushButton, QLabel
import sys
import re

PACKET_SIZE = 17   # длина посылки в байтах

class SerialHandler(QObject):
    response_ready = pyqtSignal(str, float)

    def __init__(self, port_name='COM5', baudrate=9600, bits=8, parity='N', stopbits=1):
        super().__init__()
        self.buffer = b''
        self.serial = QSerialPort()
        self.serial.setPortName(port_name)
        self.serial.setBaudRate(baudrate)
        match parity:
            case 'N': self.parity = QSerialPort.Parity.NoParity
            case 'E': self.parity = QSerialPort.Parity.EvenParity
            case 'O': self.parity = QSerialPort.Parity.OddParity
        self.serial.setParity(self.parity)
        self.serial.setDataBits(QSerialPort.DataBits.Data8)
        self.serial.setStopBits(QSerialPort.StopBits.OneStop)
        self.serial.open(QSerialPort.OpenModeFlag.ReadOnly)
        self.serial.readyRead.connect(self._read_data)
        # Регулярное выражение:
        # \s+ - один или несколько пробелов
        # (\d+\.\d+) - число с точкой (одна или более цифр, точка, одна или более цифр)
        # kN - заданный суффикс
        self.pattern = re.compile(r"\s+(\d+\.\d+)KN")

    def format_float_with_sign(self, value, total_digits, decimals) -> str:
        """
        Форматирует число с фиксированным количеством разрядов total_digits (всего),
        из которых decimals — количество знаков после запятой.
        При этом знак минуса занимает старший разряд, если число отрицательное,
        иначе знак не выводится.

        Пример: format_float_with_sign(-12.345, 8, 3) -> '-00012.345'
        """
        sign = '-' if value < 0 else ''
        abs_value = abs(value)

        # Форматируем число с нужным количеством десятичных знаков
        formatted = f"{abs_value:.{decimals}f}"

        whole, fraction = formatted.split('.')
        whole_len = total_digits - decimals - len(sign) - 1  # -1 для точки

        if whole_len < len(whole):
            raise ValueError("Число не помещается в указанное количество разрядов")

        # Заполняем целую часть нулями слева
        whole_filled = whole.zfill(whole_len)

        return f"{sign}{whole_filled}.{fraction}"

    def send_request(self):
        pass

    def _read_data(self):
        # Получаем весь пришедший ответ
        self.buffer += self.serial.readAll().data()
        while len(self.buffer) >= PACKET_SIZE:
            packet = self.buffer[:PACKET_SIZE]
            self.buffer = self.buffer[PACKET_SIZE:]
            hex_view = packet.hex(' ')
            text_view = packet.decode(errors='replace')

            text_view_kn = text_view[5:15]
            match = self.pattern.search(text_view_kn)
            if match == None:
                print(f'match NONE: {text_view}')
                self.buffer = b''
                return
            number_str = match.group(1)
            value = float(number_str)
            text = self.format_float_with_sign(value, 8, 2)
            self.response_ready.emit(text, value)

class MainWindow(QWidget):
    def __init__(self, port_name):
        super().__init__()
        self.setWindowTitle("Serial COM Request Example")
        self.layout = QVBoxLayout()
        self.label = QLabel("---------")
        self.label.setStyleSheet("""
            QLabel {
                background-color: black;
                color: #FFCC00;
                font-family: 'LCDMono2', 'Consolas', 'Courier New', monospace;
                font-size: 46pt;
            }
        """)
        self.label.setAlignment(Qt.AlignmentFlag.AlignHCenter | Qt.AlignmentFlag.AlignVCenter)

        self.layout.addWidget(self.label)
        self.setLayout(self.layout)

        self.serial_handler = SerialHandler(port_name)

        #self.button.clicked.connect(self.serial_handler.send_request)
        self.serial_handler.response_ready.connect(self.show_response)

    def show_response(self, text):
        new_text = text.replace(" ", "0")
        self.label.setText(f"{new_text}<span style='font-family: Consolas; font-size: 46pt; color: lightgreen;'> kN")

if __name__ == "__main__":
    # Замените 'COM3' на нужный порт, например '/dev/ttyUSB0' для Linux
    port_name = 'COM5'
    app = QApplication(sys.argv)
    window = MainWindow(port_name)
    window.setGeometry(300, 300, 300, 200)
    window.show()
    sys.exit(app.exec())
