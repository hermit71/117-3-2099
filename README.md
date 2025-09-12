# Stand Control GUI

Проект представляет собой графическое приложение на PyQt6 для мониторинга и управления стендом через ПЛК по протоколу Modbus TCP.

## Требования

- Python 3.10+
- Зависимости перечислены в файле [`requirements.txt`](requirements.txt):
  - PyQt6
  - pyqtgraph
  - pymodbus
  - pyyaml
  - pyqt-led

## Шаги запуска

1. (Опционально) Создайте и активируйте виртуальное окружение.
2. Установите зависимости:
   ```bash
   pip install -r requirements.txt
   ```
3. Настройте параметры подключения к ПЛК в файле [`config/config.yaml`](config/config.yaml).
4. Запустите приложение:
   ```bash
   python app.py
   ```

## Структура каталогов

```
.
├── app.py               # Точка входа GUI
├── config/              # Конфигурация подключения и параметров
│   └── config.yaml
├── modbus_registers.txt # Описание регистров ПЛК
├── requirements.txt     # Зависимости проекта
├── src/                 # Исходный код приложения
│   ├── command_handler.py
│   ├── data/
│   │   ├── model.py
│   │   └── realtime_data.py
│   ├── models/
│   │   └── modeldata.py
│   ├── ui/              # Интерфейс и виджеты
│   │   ├── main_window.py
│   │   └── ...
│   └── utils/           # Вспомогательные модули
│       └── ...
└── tmp/                 # Временные файлы и эксперименты
```

## Взаимодействие с ПЛК

Обмен данными с ПЛК осуществляется по Modbus TCP. Файл [`modbus_registers.txt`](modbus_registers.txt) содержит список регистров для обмена, что упрощает интеграцию и диагностику.

