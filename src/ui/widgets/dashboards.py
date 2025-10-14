"""Dashboard definitions used by UI widgets."""

from src.ui import labels as lbl

# Панели экрана ручного режима
hand_graphs = [
    [
        "tension plot",
        {
            "line_color": "#1C1CF0",
            "background": "#FEFEFA",
            "grid_color": "#C8C8C8",
            "line_width": 2,
            "dataset_name": "tension_data_c",
            "y_limits": (-65000.0, 65000.0),
        },
    ],
    [
        "velocity plot",
        {
            "line_color": "#1C1CF0",
            "background": "#FEFEFA",
            "grid_color": "#C8C8C8",
            "line_width": 2,
            "dataset_name": "velocity_data",
            "y_limits": (-10.0, 10.0),
        },
    ],
]

# Индикаторы состояния дискретных входов
hand_right_panel_led_dashboards = [
    ['alarm_dashboard',
     {'num': 8,
      'title': 'Контроль цепей безопасности',
      'labels': lbl.alarm_led_labels,
      'register': 0,
      'bits': [0, 1, 2, 3, 4, 5, 6, 7]}],
    ['ups_dashboard',
     {'num': 3,
      'title': 'Монитор состояния ИБП',
      'labels': lbl.ups_led_labels,
      'register': 0,
      'bits': [8, 9, 10]}],
    ['power_dashboard',
     {'num': 2,
      'title': 'Питание приводов',
      'labels': lbl.power_labels,
      'register': 0,
      'bits': [11, 12]}]
]

