"""Представление главного окна приложения на основе формы Qt Designer."""

from PyQt6 import QtCore, QtGui, QtWidgets

from src.ui.main_window_view_ui import Ui_MainWindow


class MainWindowView(Ui_MainWindow):
    """Расширяет сгенерированное представление дополнительной настройкой."""

    INIT_HEADER_BUTTON_COUNT = 3
    INIT_HEADER_BUTTON_WIDTH = 260
    INIT_HEADER_BUTTON_SPACING = 10
    INIT_FORM_MARGIN = 10
    INIT_FORM_SPACING = 12
    INIT_GROUPBOX_WIDTH = (
        INIT_HEADER_BUTTON_COUNT * INIT_HEADER_BUTTON_WIDTH
        + (INIT_HEADER_BUTTON_COUNT - 1) * INIT_HEADER_BUTTON_SPACING
    )
    INIT_FORM_AVAILABLE_WIDTH = INIT_GROUPBOX_WIDTH - 2 * INIT_FORM_MARGIN - INIT_FORM_SPACING
    INIT_LABEL_WIDTH = (INIT_FORM_AVAILABLE_WIDTH * 2) // 5
    INIT_FIELD_WIDTH = INIT_FORM_AVAILABLE_WIDTH - INIT_LABEL_WIDTH
    INIT_LABEL_MIN_HEIGHT_MULTIPLIER = 2.2

    def setup_ui(self, main_window: QtWidgets.QMainWindow) -> None:
        """Создает интерфейс и выполняет дополнительную конфигурацию."""
        super().setupUi(main_window)
        self._configure_hand_sections()
        self._configure_hand_manual_group_widgets()
        self._configure_hand_tension_group_widgets()
        self._configure_init_section()
        self.pager.setCurrentIndex(1)
        self.retranslate_ui(main_window)

    # ------------------------------------------------------------------
    # Настройка страницы ручного управления
    # ------------------------------------------------------------------
    def _configure_hand_sections(self) -> None:
        """Настраивает панели страницы ручного управления."""
        dashboard_policy = QtWidgets.QSizePolicy(
            QtWidgets.QSizePolicy.Policy.Preferred,
            QtWidgets.QSizePolicy.Policy.Fixed,
        )
        self.pageHand_pnlTopDashboard.setSizePolicy(dashboard_policy)
        self.pageHand_pnlTopDashboard.setBaseSize(QtCore.QSize(0, 120))
        self.pageHand_pnlTopDashboard.setStyleSheet(
            "background-color: rgb(242, 252, 255);"
        )
        self.pageHand_pnlTopDashboard.setFrameShape(QtWidgets.QFrame.Shape.StyledPanel)
        self.pageHand_pnlTopDashboard.setFrameShadow(QtWidgets.QFrame.Shadow.Raised)

        self.pageHand_pnlGraph.setFrameShape(QtWidgets.QFrame.Shape.StyledPanel)
        self.pageHand_pnlGraph.setFrameShadow(QtWidgets.QFrame.Shadow.Raised)

        ctrl_policy = QtWidgets.QSizePolicy(
            QtWidgets.QSizePolicy.Policy.Fixed,
            QtWidgets.QSizePolicy.Policy.Preferred,
        )
        ctrl_policy.setHeightForWidth(
            self.pageHand_pnlCtrl.sizePolicy().hasHeightForWidth()
        )
        self.pageHand_pnlCtrl.setSizePolicy(ctrl_policy)
        self.pageHand_pnlCtrl.setBaseSize(QtCore.QSize(280, 0))
        self.pageHand_pnlCtrl.setFrameShape(QtWidgets.QFrame.Shape.StyledPanel)
        self.pageHand_pnlCtrl.setFrameShadow(QtWidgets.QFrame.Shadow.Raised)
        self.verticalLayout_8.setStretch(0, 2)
        self.verticalLayout_8.setStretch(1, 3)
        self.verticalLayout_8.setStretch(2, 12)

        right_policy = QtWidgets.QSizePolicy(
            QtWidgets.QSizePolicy.Policy.Minimum,
            QtWidgets.QSizePolicy.Policy.Preferred,
        )
        right_policy.setHeightForWidth(
            self.pageHand_pnlRight.sizePolicy().hasHeightForWidth()
        )
        self.pageHand_pnlRight.setSizePolicy(right_policy)
        self.pageHand_pnlRight.setMinimumSize(QtCore.QSize(280, 0))
        self.pageHand_pnlRight.setFrameShape(QtWidgets.QFrame.Shape.StyledPanel)
        self.pageHand_pnlRight.setFrameShadow(QtWidgets.QFrame.Shadow.Raised)

    def _configure_hand_manual_group_widgets(self) -> None:
        """Настраивает элементы группы ручного управления."""
        self._configure_manual_group_container()
        self._configure_manual_group_spinbox()
        self._configure_manual_group_slider()
        self._configure_manual_group_buttons()

    def _configure_manual_group_container(self) -> None:
        """Задает параметры контейнера ручного управления."""
        size_policy = QtWidgets.QSizePolicy(
            QtWidgets.QSizePolicy.Policy.Minimum,
            QtWidgets.QSizePolicy.Policy.Minimum,
        )
        size_policy.setHeightForWidth(self.groupBox.sizePolicy().hasHeightForWidth())
        self.groupBox.setSizePolicy(size_policy)
        self.verticalLayout_9.setContentsMargins(4, 4, 4, 4)
        self.verticalLayout_9.setSpacing(4)
        self.horizontalLayout_11.setSpacing(4)

    def _configure_manual_group_spinbox(self) -> None:
        """Настраивает спинбокс ручного управления."""
        size_policy = QtWidgets.QSizePolicy(
            QtWidgets.QSizePolicy.Policy.Preferred,
            QtWidgets.QSizePolicy.Policy.Preferred,
        )
        size_policy.setHeightForWidth(
            self.dsbHandVelocity_1.sizePolicy().hasHeightForWidth()
        )
        self.dsbHandVelocity_1.setSizePolicy(size_policy)
        spin_font = QtGui.QFont()
        spin_font.setFamily("Inconsolata LGC Nerd Font")
        spin_font.setPointSize(11)
        self.dsbHandVelocity_1.setFont(spin_font)
        self.dsbHandVelocity_1.setWrapping(False)
        self.dsbHandVelocity_1.setAlignment(
            QtCore.Qt.AlignmentFlag.AlignRight
            | QtCore.Qt.AlignmentFlag.AlignTrailing
            | QtCore.Qt.AlignmentFlag.AlignVCenter
        )
        self.dsbHandVelocity_1.setButtonSymbols(
            QtWidgets.QAbstractSpinBox.ButtonSymbols.PlusMinus
        )
        self.dsbHandVelocity_1.setDecimals(1)
        self.dsbHandVelocity_1.setMaximum(60.0)
        self.dsbHandVelocity_1.setSingleStep(0.1)
        self.dsbHandVelocity_1.setProperty("value", 6.0)

    def _configure_manual_group_slider(self) -> None:
        """Задает диапазон и ориентацию ползунка скорости."""
        self.sldHandVelocity_1.setMaximum(600)
        self.sldHandVelocity_1.setProperty("value", 60)
        self.sldHandVelocity_1.setOrientation(QtCore.Qt.Orientation.Horizontal)

    def _configure_manual_group_buttons(self) -> None:
        """Настраивает кнопки пошагового движения."""
        self.btnJog_CCW.setMinimumSize(QtCore.QSize(0, 32))
        self.btnJog_CW.setMinimumSize(QtCore.QSize(0, 32))

    def _configure_hand_tension_group_widgets(self) -> None:
        """Настраивает элементы группы управления моментом."""
        tension_font = QtGui.QFont()
        tension_font.setFamily("Inconsolata LGC Nerd Font")
        tension_font.setPointSize(11)
        self._configure_tension_group_container()
        self._configure_tension_moment_controls(tension_font)
        self._configure_tension_ramp_controls(tension_font)
        self._configure_tension_time_controls(tension_font)
        self._configure_tension_aux_controls()

    def _configure_tension_group_container(self) -> None:
        """Задает параметры компоновки группы управления моментом."""
        self.verticalLayout_10.setContentsMargins(4, 4, 4, 4)
        self.verticalLayout_10.setSpacing(4)
        self.horizontalLayout_13.setSpacing(4)
        self.horizontalLayout_14.setSpacing(4)
        self.horizontalLayout_15.setSpacing(4)
        self.horizontalLayout_16.setSpacing(4)

    def _configure_tension_moment_controls(self, font: QtGui.QFont) -> None:
        """Настраивает поля и ползунки момента."""
        self.dsbHandTension.setFont(font)
        self.dsbHandTension.setAlignment(
            QtCore.Qt.AlignmentFlag.AlignRight
            | QtCore.Qt.AlignmentFlag.AlignTrailing
            | QtCore.Qt.AlignmentFlag.AlignVCenter
        )
        self.dsbHandTension.setButtonSymbols(
            QtWidgets.QAbstractSpinBox.ButtonSymbols.PlusMinus
        )
        self.dsbHandTension.setDecimals(2)
        self.dsbHandTension.setMinimum(-50.0)
        self.dsbHandTension.setMaximum(50.0)
        self.dsbHandTension.setSingleStep(0.5)

        self.sldHandTension.setMinimum(-500)
        self.sldHandTension.setMaximum(500)
        self.sldHandTension.setSingleStep(5)
        self.sldHandTension.setPageStep(50)
        self.sldHandTension.setOrientation(QtCore.Qt.Orientation.Horizontal)

    def _configure_tension_ramp_controls(self, font: QtGui.QFont) -> None:
        """Настраивает элементы управления скоростью нарастания."""
        self.dsbHandVelocity_2.setFont(font)
        self.dsbHandVelocity_2.setAlignment(
            QtCore.Qt.AlignmentFlag.AlignRight
            | QtCore.Qt.AlignmentFlag.AlignTrailing
            | QtCore.Qt.AlignmentFlag.AlignVCenter
        )
        self.dsbHandVelocity_2.setButtonSymbols(
            QtWidgets.QAbstractSpinBox.ButtonSymbols.PlusMinus
        )
        self.dsbHandVelocity_2.setDecimals(1)
        self.dsbHandVelocity_2.setMaximum(4.0)
        self.dsbHandVelocity_2.setSingleStep(0.1)
        self.dsbHandVelocity_2.setProperty("value", 1.0)

        self.sldHandVelocity_2.setMaximum(40)
        self.sldHandVelocity_2.setOrientation(QtCore.Qt.Orientation.Horizontal)

    def _configure_tension_time_controls(self, font: QtGui.QFont) -> None:
        """Настраивает элементы управления временем выдержки."""
        self.dsbHandTime_1.setFont(font)
        self.dsbHandTime_1.setAlignment(
            QtCore.Qt.AlignmentFlag.AlignRight
            | QtCore.Qt.AlignmentFlag.AlignTrailing
            | QtCore.Qt.AlignmentFlag.AlignVCenter
        )
        self.dsbHandTime_1.setButtonSymbols(
            QtWidgets.QAbstractSpinBox.ButtonSymbols.PlusMinus
        )
        self.dsbHandTime_1.setDecimals(0)
        self.dsbHandTime_1.setMaximum(60.0)
        self.dsbHandTime_1.setSingleStep(1.0)
        self.dsbHandTime_1.setProperty("value", 10.0)

    def _configure_tension_aux_controls(self) -> None:
        """Настраивает дополнительные элементы группы момента."""
        self.pushButton_2.setMinimumSize(QtCore.QSize(0, 32))
        self.pushButton_2.setBaseSize(QtCore.QSize(0, 32))

    # ------------------------------------------------------------------
    # Настройка страницы инициализации
    # ------------------------------------------------------------------
    def _configure_init_section(self) -> None:
        """Подготавливает компоновку и элементы страницы инициализации."""
        self._configure_init_layout()
        self._configure_init_groupboxes_style()
        self._configure_init_form_elements()

    def _configure_init_layout(self) -> None:
        """Настраивает параметры компоновки блока инициализации."""
        self.verticalLayout_11.setAlignment(
            QtCore.Qt.AlignmentFlag.AlignLeft | QtCore.Qt.AlignmentFlag.AlignTop
        )
        self.verticalLayout_11.setStretch(0, 4)
        self.verticalLayout_11.setStretch(1, 4)
        self.verticalLayout_11.setStretch(2, 4)
        self.verticalLayout_11.setStretch(3, 1)
        self.verticalLayout_12.setStretch(0, 1)
        self.verticalLayout_12.setStretch(1, 8)

    def _configure_init_groupboxes_style(self) -> None:
        """Настраивает стили и шрифты групповых блоков."""
        group_boxes = [self.groupBox_4, self.groupBox_5, self.groupBox_6]
        for group_box in group_boxes:
            font = QtGui.QFont()
            font.setPointSize(10)
            group_box.setFont(font)
            group_box.setStyleSheet(
                "QGroupBox { background-color: transparent; }"
                "QGroupBox::title { background-color: transparent; }"
            )

    def _configure_init_form_elements(self) -> None:
        """Настраивает поля и подписи форм на странице инициализации."""
        main_pairs = [
            ("lineEdit", "label", True, True),
            ("lineEdit_2", "label_9", False, False),
            ("lineEdit_3", "label_10", False, False),
            ("lineEdit_4", "label_11", False, False),
            ("lineEdit_5", "label_12", False, False),
            ("lineEdit_11", "label_18", False, False),
            ("lineEdit_12", "label_19", False, False),
            ("lineEdit_13", "label_20", False, False),
        ]
        sample_pairs = [
            ("lineEdit_6", "label_17", True, True),
            ("lineEdit_7", "label_13", False, False),
            ("lineEdit_8", "label_14", False, False),
            ("lineEdit_9", "label_15", False, False),
            ("lineEdit_10", "label_16", False, False),
        ]
        list_pairs = [
            ("listWidget", "label_25"),
            ("listWidget_2", "label_26"),
            ("listWidget_3", "label_27"),
        ]

        for edit_name, label_name, align_left, label_min in main_pairs:
            line_edit = getattr(self, edit_name)
            label = getattr(self, label_name)
            self._configure_form_line_edit(line_edit, align_left=align_left)
            self._configure_form_label(label, with_min_size=label_min)

        for edit_name, label_name, align_left, label_min in sample_pairs:
            line_edit = getattr(self, edit_name)
            label = getattr(self, label_name)
            self._configure_form_line_edit(line_edit, align_left=align_left)
            self._configure_form_label(label, with_min_size=label_min)

        for list_name, label_name in list_pairs:
            list_widget = getattr(self, list_name)
            label = getattr(self, label_name)
            self._configure_form_list_widget(list_widget)
            self._configure_form_label(label, with_min_size=True)

    def _configure_form_line_edit(
        self,
        line_edit: QtWidgets.QLineEdit,
        *,
        align_left: bool = False,
    ) -> None:
        """Настраивает параметры текстового поля формы."""
        size_policy = QtWidgets.QSizePolicy(
            QtWidgets.QSizePolicy.Policy.Fixed,
            QtWidgets.QSizePolicy.Policy.Fixed,
        )
        line_edit.setSizePolicy(size_policy)
        line_edit.setMinimumWidth(self.INIT_FIELD_WIDTH)
        line_edit.setMaximumWidth(self.INIT_FIELD_WIDTH)
        font = QtGui.QFont()
        font.setPointSize(10)
        line_edit.setFont(font)
        line_edit.ensurePolished()
        base_height = line_edit.sizeHint().height()
        if base_height > 0:
            increased_height = max(int(base_height * 1.1), base_height + 1)
            line_edit.setFixedHeight(increased_height)
        else:
            metrics = line_edit.fontMetrics()
            fallback_height = max(int(metrics.lineSpacing() * 1.1), 1)
            line_edit.setFixedHeight(fallback_height)
        if align_left:
            line_edit.setAlignment(
                QtCore.Qt.AlignmentFlag.AlignLeading
                | QtCore.Qt.AlignmentFlag.AlignLeft
                | QtCore.Qt.AlignmentFlag.AlignVCenter
            )

    def _configure_form_label(
        self,
        label: QtWidgets.QLabel,
        *,
        with_min_size: bool = False,
    ) -> None:
        """Настраивает параметры подписи поля формы."""
        font = QtGui.QFont()
        font.setPointSize(10)
        label.setFont(font)
        label.setWordWrap(True)
        label.setAlignment(
            QtCore.Qt.AlignmentFlag.AlignRight
            | QtCore.Qt.AlignmentFlag.AlignVCenter
        )
        size_policy = QtWidgets.QSizePolicy(
            QtWidgets.QSizePolicy.Policy.Fixed,
            QtWidgets.QSizePolicy.Policy.Preferred,
        )
        label.setSizePolicy(size_policy)
        label.setMinimumWidth(self.INIT_LABEL_WIDTH)
        label.setMaximumWidth(self.INIT_LABEL_WIDTH)
        metrics = label.fontMetrics()
        base_line = max(metrics.lineSpacing(), 1)
        min_height = max(
            int(base_line * self.INIT_LABEL_MIN_HEIGHT_MULTIPLIER),
            base_line,
        )
        if with_min_size:
            min_height = max(
                min_height,
                int(base_line * (self.INIT_LABEL_MIN_HEIGHT_MULTIPLIER + 0.2)),
            )
        label.setMinimumHeight(min_height)

    def _configure_form_list_widget(self, list_widget: QtWidgets.QListWidget) -> None:
        """Настраивает параметры списка выбора."""
        size_policy = QtWidgets.QSizePolicy(
            QtWidgets.QSizePolicy.Policy.Fixed,
            QtWidgets.QSizePolicy.Policy.Maximum,
        )
        list_widget.setSizePolicy(size_policy)
        list_widget.setMinimumWidth(self.INIT_FIELD_WIDTH)
        list_widget.setMaximumWidth(self.INIT_FIELD_WIDTH)
        list_widget.setMaximumHeight(25)
        font = QtGui.QFont()
        font.setPointSize(10)
        list_widget.setFont(font)

    def _finalize_init_groupboxes(self) -> None:
        """Фиксирует размеры информационных блоков инициализации."""
        group_boxes = [self.groupBox_4, self.groupBox_5, self.groupBox_6]
        boxes = [box for box in group_boxes if box is not None]
        if not boxes:
            return

        target_width = self.INIT_GROUPBOX_WIDTH
        for box in boxes:
            box.ensurePolished()
            box.setSizePolicy(
                QtWidgets.QSizePolicy.Policy.Fixed,
                QtWidgets.QSizePolicy.Policy.Fixed,
            )
            box.setMinimumWidth(target_width)
            box.setMaximumWidth(target_width)

            layout = box.layout()
            if layout is not None:
                layout.activate()
            size_hint = box.sizeHint()
            height_hint = size_hint.height()
            if height_hint <= 0:
                height_hint = box.minimumSizeHint().height()
            box.setMinimumHeight(max(height_hint, 1))
            box.setMaximumHeight(max(height_hint, 1))
            box.adjustSize()

    # ------------------------------------------------------------------
    # Перевод интерфейса
    # ------------------------------------------------------------------
    def retranslate_ui(self, main_window: QtWidgets.QMainWindow) -> None:
        """Применяет текстовые ресурсы и уточняет единицы измерения."""
        super().retranslateUi(main_window)
        translate = QtCore.QCoreApplication.translate
        self.dsbHandVelocity_1.setSuffix(translate("MainWindow", "°/мин"))
        self.dsbHandTension.setSuffix(translate("MainWindow", " Нм"))
        self.dsbHandVelocity_2.setSuffix(translate("MainWindow", " Нм/с"))
        self.dsbHandTime_1.setSuffix(translate("MainWindow", " с"))
        self._finalize_init_groupboxes()
