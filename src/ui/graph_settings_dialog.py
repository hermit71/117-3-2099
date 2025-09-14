"""Dialog for editing graph appearance settings."""

from PyQt6.QtWidgets import (
    QDialog,
    QDialogButtonBox,
    QFormLayout,
    QGroupBox,
    QPushButton,
    QSpinBox,
    QVBoxLayout,
    QColorDialog,
)


class GraphSettingsDialog(QDialog):
    """Allow the user to customize graph colors and line width."""

    def __init__(self, parent, config, plots_description, graph_widgets):
        super().__init__(parent)
        self.config = config
        self.plots_description = plots_description
        self.graph_widgets = graph_widgets
        self.setWindowTitle("Настройки графиков")

        self.controls = []
        layout = QVBoxLayout(self)
        for name, desc in plots_description:
            group = QGroupBox(name, self)
            form = QFormLayout(group)

            btn_line = QPushButton()
            btn_bg = QPushButton()
            btn_grid = QPushButton()
            spin_width = QSpinBox()
            spin_width.setRange(1, 4)

            cfg = config.get("graphs", name, {})
            line_color = cfg.get("line_color", desc["line_color"])
            background = cfg.get("background", desc["background"])
            grid_color = cfg.get("grid_color", desc["grid_color"])
            line_width = cfg.get("line_width", desc["line_width"])

            for btn, color in (
                (btn_line, line_color),
                (btn_bg, background),
                (btn_grid, grid_color),
            ):
                btn.setProperty("color", color)
                btn.setStyleSheet(f"background-color: {color}")
                btn.clicked.connect(lambda _, b=btn: self._choose_color(b))
            spin_width.setValue(line_width)

            form.addRow("Цвет линии", btn_line)
            form.addRow("Цвет фона", btn_bg)
            form.addRow("Цвет сетки", btn_grid)
            form.addRow("Толщина линии", spin_width)
            group.setLayout(form)
            layout.addWidget(group)

            self.controls.append(
                {
                    "name": name,
                    "btn_line": btn_line,
                    "btn_bg": btn_bg,
                    "btn_grid": btn_grid,
                    "spin": spin_width,
                }
            )

        buttons = QDialogButtonBox(
            QDialogButtonBox.StandardButton.Ok | QDialogButtonBox.StandardButton.Cancel
        )
        buttons.accepted.connect(self.accept)
        buttons.rejected.connect(self.reject)
        layout.addWidget(buttons)

    def _choose_color(self, button):
        color = QColorDialog.getColor(parent=self)
        if color.isValid():
            button.setProperty("color", color.name())
            button.setStyleSheet(f"background-color: {color.name()}")

    def accept(self):
        self.config.cfg.setdefault("graphs", {})
        for idx, ctrl in enumerate(self.controls):
            name = ctrl["name"]
            line_color = ctrl["btn_line"].property("color")
            background = ctrl["btn_bg"].property("color")
            grid_color = ctrl["btn_grid"].property("color")
            line_width = ctrl["spin"].value()
            self.config.cfg["graphs"][name] = {
                "line_color": line_color,
                "background": background,
                "grid_color": grid_color,
                "line_width": line_width,
            }
            desc = self.plots_description[idx][1]
            desc.update(
                {
                    "line_color": line_color,
                    "background": background,
                    "grid_color": grid_color,
                    "line_width": line_width,
                }
            )
            self.graph_widgets[idx].apply_style(
                line_color=line_color,
                background=background,
                grid_color=grid_color,
                line_width=line_width,
            )
        self.config.save()
        super().accept()
