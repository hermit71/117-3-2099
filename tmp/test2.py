import sys
import time
import numpy as np
from pyqtgraph.Qt import QtWidgets
import pyqtgraph as pg

# Класс основного приложения
class MainWindow(QtWidgets.QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Пример ProgressDialog в PyQtGraph")
        self.resize(400, 300)

        # Создаём центральный виджет и layout
        central_widget = QtWidgets.QWidget()
        self.setCentralWidget(central_widget)
        layout = QtWidgets.QVBoxLayout(central_widget)

        # Кнопка для запуска процесса с ProgressDialog
        self.start_button = QtWidgets.QPushButton("Запустить задачу")
        self.start_button.clicked.connect(self.run_task)
        layout.addWidget(self.start_button)

    def run_task(self):
        # Создаём ProgressDialog
        progress_dialog = pg.ProgressDialog(
            "Выполняется длительная задача...", 
            cancelText="Отмена",  # Текст кнопки отмены
            maximum=100,           # Максимальное значение прогресса
            wait=0,               # Время ожидания перед показом (0 = сразу)
            parent=self
        )

        # Симулируем длительную задачу
        for i in range(101):
            # Обновляем значение прогресса
            progress_dialog.setValue(i)

            # Проверяем, была ли нажата кнопка отмены
            if progress_dialog.wasCanceled():
                print("Задача отменена пользователем")
                break

            # Имитация работы (например, обработка данных)
            time.sleep(0.1)  # Задержка для демонстрации

            # Пример обработки данных (здесь просто вычисление для примера)
            _ = np.sin(np.linspace(0, 2 * np.pi, 1000))

        # Завершаем ProgressDialog
        progress_dialog.setValue(100)  # Устанавливаем 100% для завершения
        if not progress_dialog.wasCanceled():
            print("Задача завершена успешно")

# Запуск приложения
if __name__ == '__main__':
    app = QtWidgets.QApplication(sys.argv)
    window = MainWindow()
    window.show()
    sys.exit(app.exec())