"""Построение главного окна приложения программно."""

from PyQt6 import QtCore, QtGui, QtWidgets

from src.ui.widgets.graph_widget import GraphWidget
from src.ui.widgets.hand_graph_panel import HandGraphPanel
from src.ui.widgets.hand_right_panel import LedDashboardPanel
from src.ui.widgets.hand_top_panel import DashboardPanel
from src.utils.spin_box_int_to_float import AppSpinBox


class MainWindowView:
    """Формирует графический интерфейс главного окна приложения."""

    def setup_ui(self, MainWindow: QtWidgets.QMainWindow) -> None:
        """Создает и настраивает все элементы пользовательского интерфейса."""
        # === Настройка основного окна и создание каркаса ===
        self._configure_main_window(MainWindow)
        self._build_central_area(MainWindow)

        # === Боковая панель управления испытаниями ===
        self._build_left_panel()

        # === Основная рабочая область и страницы интерфейса ===
        self._build_base_panel()
        self._create_hand_page()
        self._create_init_page()
        self._create_static1_page()
        self._create_static2_page()
        self._create_calibration_page()
        self._create_protocol_page()
        self._create_archive_page()
        self._create_service_page()

        # === Завершение сборки и подключение сигналов ===
        self._finalize_main_layout(MainWindow)
        self._create_menu_bar(MainWindow)
        self._connect_signals(MainWindow)

        self.retranslate_ui(MainWindow)
        self.pager.setCurrentIndex(1)

    def _configure_main_window(self, main_window: QtWidgets.QMainWindow) -> None:
        """Задает базовые параметры главного окна."""
        main_window.setObjectName("MainWindow")
        main_window.setWindowModality(QtCore.Qt.WindowModality.NonModal)
        main_window.resize(1743, 999)
        main_window.setToolButtonStyle(
            QtCore.Qt.ToolButtonStyle.ToolButtonTextBesideIcon
        )

    def _build_central_area(self, main_window: QtWidgets.QMainWindow) -> None:
        """Создает центральный виджет и основной макет окна."""
        # --- Объявление виджетов ---
        self.centralwidget = QtWidgets.QWidget(parent=main_window)
        self.verticalLayout = QtWidgets.QVBoxLayout(self.centralwidget)
        self.base_widget = QtWidgets.QWidget(parent=self.centralwidget)
        self.horizontalLayout = QtWidgets.QHBoxLayout(self.base_widget)

        # --- Настройка свойств ---
        self.centralwidget.setObjectName("centralwidget")
        self.centralwidget.setStyleSheet("background-color: rgb(254, 254, 250);")

        self.verticalLayout.setContentsMargins(4, 4, 4, 4)
        self.verticalLayout.setSpacing(4)
        self.verticalLayout.setObjectName("verticalLayout")

        self.base_widget.setObjectName("base_widget")

        self.horizontalLayout.setContentsMargins(4, 4, 4, 4)
        self.horizontalLayout.setSpacing(4)
        self.horizontalLayout.setObjectName("horizontalLayout")

        # --- Формирование иерархии ---
        self.verticalLayout.addWidget(self.base_widget)

    def _build_left_panel(self) -> None:
        """Формирует левую панель навигации и управления испытанием."""
        self._declare_left_panel_containers()
        self._configure_left_panel_containers()

        navigation_buttons, control_buttons = self._declare_navigation_buttons()
        self._configure_navigation_buttons(navigation_buttons, control_buttons)
        self._assemble_navigation_buttons(navigation_buttons, control_buttons)

        self.horizontalLayout.addWidget(self.left_panel)

    def _declare_left_panel_containers(self) -> None:
        """Создает каркас левой панели."""
        self.left_panel = QtWidgets.QFrame(parent=self.base_widget)
        self.verticalLayout_3 = QtWidgets.QVBoxLayout(self.left_panel)
        self.verticalLayout_2 = QtWidgets.QVBoxLayout()

    def _configure_left_panel_containers(self) -> None:
        """Настраивает контейнеры левой панели."""
        size_policy = QtWidgets.QSizePolicy(
            QtWidgets.QSizePolicy.Policy.Minimum,
            QtWidgets.QSizePolicy.Policy.Preferred,
        )
        size_policy.setHeightForWidth(self.left_panel.sizePolicy().hasHeightForWidth())
        self.left_panel.setSizePolicy(size_policy)
        self.left_panel.setMinimumSize(QtCore.QSize(220, 0))
        self.left_panel.setFrameShape(QtWidgets.QFrame.Shape.StyledPanel)
        self.left_panel.setFrameShadow(QtWidgets.QFrame.Shadow.Raised)
        self.left_panel.setObjectName("left_panel")

        self.verticalLayout_3.setContentsMargins(0, 0, 0, 0)
        self.verticalLayout_3.setSpacing(4)
        self.verticalLayout_3.setObjectName("verticalLayout_3")

        self.verticalLayout_2.setContentsMargins(10, 10, 10, 10)
        self.verticalLayout_2.setSpacing(10)
        self.verticalLayout_2.setObjectName("verticalLayout_2")

    def _declare_navigation_buttons(self) -> tuple[
        list[QtWidgets.QPushButton],
        list[QtWidgets.QPushButton],
    ]:
        """Создает кнопки левой панели и группирует их по назначению."""
        nav_names = [
            "btnInit",
            "btnStatic1",
            "btnStatic2",
            "btnHand",
            "btnCalibration",
            "btnProtocol",
            "btnArchive",
            "btnService",
        ]
        control_names = [
            "btnStart",
            "btnPause",
            "btnStop",
            "btnEmergencyReset",
        ]

        navigation_buttons = [self._create_panel_button(name) for name in nav_names]
        control_buttons = [self._create_panel_button(name) for name in control_names]
        return navigation_buttons, control_buttons

    def _create_panel_button(self, object_name: str) -> QtWidgets.QPushButton:
        """Создает кнопку для левой панели и сохраняет ссылку на нее."""
        button = QtWidgets.QPushButton(parent=self.left_panel)
        button.setObjectName(object_name)
        setattr(self, object_name, button)
        return button

    def _configure_navigation_buttons(
        self,
        navigation_buttons: list[QtWidgets.QPushButton],
        control_buttons: list[QtWidgets.QPushButton],
    ) -> None:
        """Настраивает свойства кнопок левой панели."""
        button_font = QtGui.QFont()
        button_font.setPointSize(10)

        for button in navigation_buttons + control_buttons:
            button.setMinimumSize(QtCore.QSize(0, 42))
            button.setFont(button_font)

        self.btnStart.setCheckable(True)
        self.btnPause.setEnabled(False)
        self.btnPause.setCheckable(True)
        self.btnStop.setCheckable(False)


    def _assemble_navigation_buttons(
        self,
        navigation_buttons: list[QtWidgets.QPushButton],
        control_buttons: list[QtWidgets.QPushButton],
    ) -> None:
        """Добавляет кнопки в макет панели."""
        for button in navigation_buttons:
            self.verticalLayout_2.addWidget(button)

        spacer = QtWidgets.QSpacerItem(
            20,
            40,
            QtWidgets.QSizePolicy.Policy.Minimum,
            QtWidgets.QSizePolicy.Policy.Expanding,
        )
        self.verticalLayout_2.addItem(spacer)

        for button in control_buttons:
            self.verticalLayout_2.addWidget(button)

        self.verticalLayout_3.addLayout(self.verticalLayout_2)

    def _build_base_panel(self) -> None:
        """Создает правую часть окна с пейджером и рабочими панелями."""
        self.base_panel = QtWidgets.QWidget(parent=self.base_widget)
        self.horizontalLayout_2 = QtWidgets.QHBoxLayout(self.base_panel)
        self.pager = QtWidgets.QStackedWidget(parent=self.base_panel)

        self.base_panel.setObjectName("base_panel")
        self.horizontalLayout_2.setContentsMargins(0, 0, 0, 0)
        self.horizontalLayout_2.setSpacing(4)
        self.horizontalLayout_2.setObjectName("horizontalLayout_2")

        self.pager.setLineWidth(0)
        self.pager.setObjectName("pager")

        self.horizontalLayout_2.addWidget(self.pager)
        self.horizontalLayout.addWidget(self.base_panel)

    def _create_hand_page(self) -> None:
        """Формирует страницу режима ручного управления."""
        self._declare_hand_page_base()
        self._build_hand_dashboard()
        self._build_hand_graph_section()
        self._declare_hand_control_panel()
        self._build_hand_servo_group()
        self._declare_hand_manual_group_widgets()
        self._configure_hand_manual_group_widgets()
        self._assemble_hand_manual_group_layout()
        self._declare_hand_tension_group_widgets()
        self._configure_hand_tension_group_widgets()
        self._assemble_hand_tension_group_layout()
        self._build_hand_right_panel()
        self._compose_hand_page()
        self.pager.addWidget(self.pageHand)

    def _declare_hand_page_base(self) -> None:
        """Создает базовые контейнеры страницы ручного управления."""
        self.pageHand = QtWidgets.QWidget()
        self.horizontalLayout_8 = QtWidgets.QHBoxLayout(self.pageHand)
        self.horizontalLayout_7 = QtWidgets.QHBoxLayout()
        self.verticalLayout_4 = QtWidgets.QVBoxLayout()
        self.widget = QtWidgets.QWidget(parent=self.pageHand)
        self.verticalLayout_5 = QtWidgets.QVBoxLayout(self.widget)
        self.horizontalLayout_9 = QtWidgets.QHBoxLayout()

        self.pageHand.setObjectName("pageHand")
        self.horizontalLayout_8.setContentsMargins(0, 0, 0, 0)
        self.horizontalLayout_8.setSpacing(4)
        self.horizontalLayout_8.setObjectName("horizontalLayout_8")

        self.horizontalLayout_7.setSpacing(4)
        self.horizontalLayout_7.setObjectName("horizontalLayout_7")

        self.verticalLayout_4.setSpacing(4)
        self.verticalLayout_4.setObjectName("verticalLayout_4")

        self.widget.setObjectName("widget")
        self.verticalLayout_5.setContentsMargins(0, 0, 0, 0)
        self.verticalLayout_5.setSpacing(4)
        self.verticalLayout_5.setObjectName("verticalLayout_5")

        self.horizontalLayout_9.setSpacing(4)
        self.horizontalLayout_9.setObjectName("horizontalLayout_9")

    def _build_hand_dashboard(self) -> None:
        """Создает верхнюю панель приборов."""
        self.pageHand_pnlTopDashboard = DashboardPanel(parent=self.pageHand)
        self.horizontalLayout_10 = QtWidgets.QHBoxLayout(self.pageHand_pnlTopDashboard)

        size_policy = QtWidgets.QSizePolicy(
            QtWidgets.QSizePolicy.Policy.Preferred,
            QtWidgets.QSizePolicy.Policy.Fixed,
        )
        size_policy.setHeightForWidth(
            self.pageHand_pnlTopDashboard.sizePolicy().hasHeightForWidth()
        )
        self.pageHand_pnlTopDashboard.setSizePolicy(size_policy)
        self.pageHand_pnlTopDashboard.setBaseSize(QtCore.QSize(0, 120))
        self.pageHand_pnlTopDashboard.setStyleSheet(
            "background-color: rgb(242, 252, 255);"
        )
        self.pageHand_pnlTopDashboard.setFrameShape(QtWidgets.QFrame.Shape.StyledPanel)
        self.pageHand_pnlTopDashboard.setFrameShadow(QtWidgets.QFrame.Shadow.Raised)
        self.pageHand_pnlTopDashboard.setObjectName("pageHand_pnlTopDashboard")
        self.horizontalLayout_10.setObjectName("horizontalLayout_10")

    def _build_hand_graph_section(self) -> None:
        """Создает область отображения графиков."""
        self.pageHand_pnlGraph = HandGraphPanel(parent=self.widget)
        self.verticalLayout_7 = QtWidgets.QVBoxLayout(self.pageHand_pnlGraph)
        self.verticalLayout_6 = QtWidgets.QVBoxLayout()
        self.graph_tension = GraphWidget(parent=self.pageHand_pnlGraph)
        self.graph_velocity = GraphWidget(parent=self.pageHand_pnlGraph)

        self.pageHand_pnlGraph.setFrameShape(QtWidgets.QFrame.Shape.StyledPanel)
        self.pageHand_pnlGraph.setFrameShadow(QtWidgets.QFrame.Shadow.Raised)
        self.pageHand_pnlGraph.setObjectName("pageHand_pnlGraph")

        self.verticalLayout_7.setObjectName("verticalLayout_7")
        self.verticalLayout_6.setObjectName("verticalLayout_6")

        self.graph_tension.setObjectName("graph_tension")
        self.graph_velocity.setObjectName("graph_velocity")

        self.verticalLayout_6.addWidget(self.graph_tension)
        self.verticalLayout_6.addWidget(self.graph_velocity)
        self.verticalLayout_7.addLayout(self.verticalLayout_6)

    def _declare_hand_control_panel(self) -> None:
        """Создает контейнер для панели управления приводом."""
        self.pageHand_pnlCtrl = QtWidgets.QFrame(parent=self.widget)
        self.verticalLayout_8 = QtWidgets.QVBoxLayout(self.pageHand_pnlCtrl)

        size_policy = QtWidgets.QSizePolicy(
            QtWidgets.QSizePolicy.Policy.Fixed,
            QtWidgets.QSizePolicy.Policy.Preferred,
        )
        size_policy.setHeightForWidth(self.pageHand_pnlCtrl.sizePolicy().hasHeightForWidth())
        self.pageHand_pnlCtrl.setSizePolicy(size_policy)
        self.pageHand_pnlCtrl.setBaseSize(QtCore.QSize(280, 0))
        self.pageHand_pnlCtrl.setFrameShape(QtWidgets.QFrame.Shape.StyledPanel)
        self.pageHand_pnlCtrl.setFrameShadow(QtWidgets.QFrame.Shadow.Raised)
        self.pageHand_pnlCtrl.setObjectName("pageHand_pnlCtrl")

        self.verticalLayout_8.setContentsMargins(4, 4, 4, 4)
        self.verticalLayout_8.setSpacing(4)
        self.verticalLayout_8.setObjectName("verticalLayout_8")

    def _build_hand_servo_group(self) -> None:
        """Формирует блок включения сервопривода."""
        self.groupBox_3 = QtWidgets.QGroupBox(parent=self.pageHand_pnlCtrl)
        self.btnServoPower = QtWidgets.QPushButton(parent=self.groupBox_3)

        self.groupBox_3.setMinimumSize(QtCore.QSize(0, 80))
        self.groupBox_3.setBaseSize(QtCore.QSize(0, 100))
        self.groupBox_3.setObjectName("groupBox_3")

        self.btnServoPower.setGeometry(QtCore.QRect(20, 30, 120, 32))
        self.btnServoPower.setObjectName("btnServoPower")

        self.verticalLayout_8.addWidget(self.groupBox_3)

    def _declare_hand_manual_group_widgets(self) -> None:
        """Объявляет элементы группы ручного управления."""
        self.groupBox = QtWidgets.QGroupBox(parent=self.pageHand_pnlCtrl)
        self.verticalLayout_9 = QtWidgets.QVBoxLayout(self.groupBox)
        self.horizontalLayout_11 = QtWidgets.QHBoxLayout()
        self.label_5 = QtWidgets.QLabel(parent=self.groupBox)
        self.dsbHandVelocity_1 = AppSpinBox(parent=self.groupBox)
        self.sldHandVelocity_1 = QtWidgets.QSlider(parent=self.groupBox)
        self.horizontalLayout_12 = QtWidgets.QHBoxLayout()
        self.btnJog_CCW = QtWidgets.QPushButton(parent=self.groupBox)
        self.btnJog_CW = QtWidgets.QPushButton(parent=self.groupBox)
        self._manual_group_spacer = QtWidgets.QSpacerItem(
            20,
            20,
            QtWidgets.QSizePolicy.Policy.Minimum,
            QtWidgets.QSizePolicy.Policy.Expanding,
        )

    def _configure_hand_manual_group_widgets(self) -> None:
        """Настраивает свойства элементов ручного управления."""
        self._configure_manual_group_container()
        self._configure_manual_group_spinbox()
        self._configure_manual_group_slider()
        self._configure_manual_group_buttons()

    def _configure_manual_group_container(self) -> None:
        size_policy = QtWidgets.QSizePolicy(
            QtWidgets.QSizePolicy.Policy.Minimum,
            QtWidgets.QSizePolicy.Policy.Minimum,
        )
        size_policy.setHeightForWidth(self.groupBox.sizePolicy().hasHeightForWidth())
        self.groupBox.setSizePolicy(size_policy)
        self.groupBox.setObjectName("groupBox")

        self.verticalLayout_9.setContentsMargins(4, 4, 4, 4)
        self.verticalLayout_9.setSpacing(4)
        self.verticalLayout_9.setObjectName("verticalLayout_9")

        self.horizontalLayout_11.setSpacing(4)
        self.horizontalLayout_11.setObjectName("horizontalLayout_11")
        self.label_5.setObjectName("label_5")

    def _configure_manual_group_spinbox(self) -> None:
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
        self.dsbHandVelocity_1.setObjectName("dsbHandVelocity_1")

    def _configure_manual_group_slider(self) -> None:
        self.sldHandVelocity_1.setMaximum(600)
        self.sldHandVelocity_1.setProperty("value", 60)
        self.sldHandVelocity_1.setOrientation(QtCore.Qt.Orientation.Horizontal)
        self.sldHandVelocity_1.setObjectName("sldHandVelocity_1")

    def _configure_manual_group_buttons(self) -> None:
        self.horizontalLayout_12.setObjectName("horizontalLayout_12")
        self.btnJog_CCW.setMinimumSize(QtCore.QSize(0, 32))
        self.btnJog_CCW.setObjectName("btnJog_CCW")
        self.btnJog_CW.setMinimumSize(QtCore.QSize(0, 32))
        self.btnJog_CW.setObjectName("btnJog_CW")

    def _assemble_hand_manual_group_layout(self) -> None:
        """Добавляет элементы группы ручного управления в компоновку."""
        self.horizontalLayout_11.addWidget(self.label_5)
        self.horizontalLayout_11.addWidget(self.dsbHandVelocity_1)
        self.verticalLayout_9.addLayout(self.horizontalLayout_11)
        self.verticalLayout_9.addWidget(self.sldHandVelocity_1)

        self.horizontalLayout_12.addWidget(self.btnJog_CCW)
        self.horizontalLayout_12.addWidget(self.btnJog_CW)
        self.verticalLayout_9.addLayout(self.horizontalLayout_12)
        self.verticalLayout_9.addItem(self._manual_group_spacer)

        self.verticalLayout_8.addWidget(self.groupBox)

    def _declare_hand_tension_group_widgets(self) -> None:
        """Объявляет элементы группы управления моментом."""
        self.groupBox_2 = QtWidgets.QGroupBox(parent=self.pageHand_pnlCtrl)
        self.verticalLayout_10 = QtWidgets.QVBoxLayout(self.groupBox_2)
        self.horizontalLayout_13 = QtWidgets.QHBoxLayout()
        self.label_6 = QtWidgets.QLabel(parent=self.groupBox_2)
        self.dsbHandTension = AppSpinBox(parent=self.groupBox_2)
        self.sldHandTension = QtWidgets.QSlider(parent=self.groupBox_2)
        self.horizontalLayout_14 = QtWidgets.QHBoxLayout()
        self.label_7 = QtWidgets.QLabel(parent=self.groupBox_2)
        self.dsbHandVelocity_2 = AppSpinBox(parent=self.groupBox_2)
        self.sldHandVelocity_2 = QtWidgets.QSlider(parent=self.groupBox_2)
        self.horizontalLayout_15 = QtWidgets.QHBoxLayout()
        self.label_8 = QtWidgets.QLabel(parent=self.groupBox_2)
        self.dsbHandTime_1 = AppSpinBox(parent=self.groupBox_2)
        self.pushButton_2 = QtWidgets.QPushButton(parent=self.groupBox_2)
        self.horizontalLayout_16 = QtWidgets.QHBoxLayout()
        self.btnHandRegSettings = QtWidgets.QToolButton(parent=self.groupBox_2)
        self.toolButton_2 = QtWidgets.QToolButton(parent=self.groupBox_2)
        self._hand_tension_spacer = QtWidgets.QSpacerItem(
            20,
            40,
            QtWidgets.QSizePolicy.Policy.Minimum,
            QtWidgets.QSizePolicy.Policy.Expanding,
        )
        self._hand_tension_btn_spacer = QtWidgets.QSpacerItem(
            40,
            20,
            QtWidgets.QSizePolicy.Policy.Expanding,
            QtWidgets.QSizePolicy.Policy.Minimum,
        )
    def _configure_hand_tension_group_widgets(self) -> None:
        """Настраивает свойства элементов группы управления моментом."""
        tension_font = QtGui.QFont()
        tension_font.setFamily("Inconsolata LGC Nerd Font")
        tension_font.setPointSize(11)

        self._configure_tension_group_container()
        self._configure_tension_moment_controls(tension_font)
        self._configure_tension_ramp_controls(tension_font)
        self._configure_tension_time_controls(tension_font)
        self._configure_tension_aux_controls()

    def _configure_tension_group_container(self) -> None:
        self.groupBox_2.setObjectName("groupBox_2")
        self.verticalLayout_10.setObjectName("verticalLayout_10")
        self.horizontalLayout_13.setObjectName("horizontalLayout_13")
        self.label_6.setObjectName("label_6")
        self.horizontalLayout_14.setObjectName("horizontalLayout_14")
        self.label_7.setObjectName("label_7")
        self.horizontalLayout_15.setObjectName("horizontalLayout_15")
        self.label_8.setObjectName("label_8")
        self.horizontalLayout_16.setObjectName("horizontalLayout_16")
        self.btnHandRegSettings.setObjectName("btnHandRegSettings")
        self.toolButton_2.setObjectName("toolButton_2")

    def _configure_tension_moment_controls(self, font: QtGui.QFont) -> None:
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
        self.dsbHandTension.setObjectName("dsbHandTension")

        self.sldHandTension.setMinimum(-500)
        self.sldHandTension.setMaximum(500)
        self.sldHandTension.setSingleStep(5)
        self.sldHandTension.setPageStep(50)
        self.sldHandTension.setOrientation(QtCore.Qt.Orientation.Horizontal)
        self.sldHandTension.setObjectName("sldHandTension")

    def _configure_tension_ramp_controls(self, font: QtGui.QFont) -> None:
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
        self.dsbHandVelocity_2.setObjectName("dsbHandVelocity_2")

        self.sldHandVelocity_2.setMaximum(40)
        self.sldHandVelocity_2.setOrientation(QtCore.Qt.Orientation.Horizontal)
        self.sldHandVelocity_2.setObjectName("sldHandVelocity_2")

    def _configure_tension_time_controls(self, font: QtGui.QFont) -> None:
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
        self.dsbHandTime_1.setObjectName("dsbHandTime_1")

    def _configure_tension_aux_controls(self) -> None:
        self.pushButton_2.setMinimumSize(QtCore.QSize(0, 32))
        self.pushButton_2.setBaseSize(QtCore.QSize(0, 32))
        self.pushButton_2.setObjectName("pushButton_2")

    def _assemble_hand_tension_group_layout(self) -> None:
        """Размещает элементы группы управления моментом."""
        self.horizontalLayout_13.addWidget(self.label_6)
        self.horizontalLayout_13.addWidget(self.dsbHandTension)
        self.verticalLayout_10.addLayout(self.horizontalLayout_13)
        self.verticalLayout_10.addWidget(self.sldHandTension)

        self.horizontalLayout_14.addWidget(self.label_7)
        self.horizontalLayout_14.addWidget(self.dsbHandVelocity_2)
        self.verticalLayout_10.addLayout(self.horizontalLayout_14)
        self.verticalLayout_10.addWidget(self.sldHandVelocity_2)

        self.horizontalLayout_15.addWidget(self.label_8)
        self.horizontalLayout_15.addWidget(self.dsbHandTime_1)
        self.verticalLayout_10.addLayout(self.horizontalLayout_15)

        self.verticalLayout_10.addWidget(self.pushButton_2)

        self.horizontalLayout_16.addWidget(self.btnHandRegSettings)
        self.horizontalLayout_16.addWidget(self.toolButton_2)
        self.horizontalLayout_16.addItem(self._hand_tension_btn_spacer)
        self.verticalLayout_10.addLayout(self.horizontalLayout_16)

        self.verticalLayout_10.addItem(self._hand_tension_spacer)
        self.verticalLayout_8.addWidget(self.groupBox_2)
        self.verticalLayout_8.setStretch(0, 2)
        self.verticalLayout_8.setStretch(1, 3)
        self.verticalLayout_8.setStretch(2, 12)

    def _build_hand_right_panel(self) -> None:
        """Создает правую панель индикации."""
        self.pageHand_pnlRight = LedDashboardPanel(parent=self.pageHand)
        size_policy = QtWidgets.QSizePolicy(
            QtWidgets.QSizePolicy.Policy.Minimum,
            QtWidgets.QSizePolicy.Policy.Preferred,
        )
        size_policy.setHeightForWidth(
            self.pageHand_pnlRight.sizePolicy().hasHeightForWidth()
        )
        self.pageHand_pnlRight.setSizePolicy(size_policy)
        self.pageHand_pnlRight.setMinimumSize(QtCore.QSize(280, 0))
        self.pageHand_pnlRight.setFrameShape(QtWidgets.QFrame.Shape.StyledPanel)
        self.pageHand_pnlRight.setFrameShadow(QtWidgets.QFrame.Shadow.Raised)
        self.pageHand_pnlRight.setObjectName("pageHand_pnlRight")

    def _compose_hand_page(self) -> None:
        """Собирает иерархию элементов страницы ручного управления."""
        self.verticalLayout_4.addWidget(self.pageHand_pnlTopDashboard)

        self.horizontalLayout_9.addWidget(self.pageHand_pnlGraph)
        self.horizontalLayout_9.addWidget(self.pageHand_pnlCtrl)
        self.horizontalLayout_9.setStretch(0, 14)
        self.horizontalLayout_9.setStretch(1, 6)

        self.verticalLayout_5.addLayout(self.horizontalLayout_9)
        self.verticalLayout_4.addWidget(self.widget)
        self.verticalLayout_4.setStretch(0, 2)
        self.verticalLayout_4.setStretch(1, 14)

        self.horizontalLayout_7.addLayout(self.verticalLayout_4)
        self.horizontalLayout_7.addWidget(self.pageHand_pnlRight)
        self.horizontalLayout_7.setStretch(0, 12)
        self.horizontalLayout_7.setStretch(1, 2)

        self.horizontalLayout_8.addLayout(self.horizontalLayout_7)

    def _create_init_page(self) -> None:
        """Формирует страницу инициализации испытания."""
        self._declare_init_page_base()
        self._build_init_header()
        self._build_init_content()
        self.pager.addWidget(self.pageInit)

    def _declare_init_page_base(self) -> None:
        """Создает каркас страницы инициализации."""
        self.pageInit = QtWidgets.QWidget()
        self.verticalLayout_13 = QtWidgets.QVBoxLayout(self.pageInit)
        self.verticalLayout_12 = QtWidgets.QVBoxLayout()

        self.pageInit.setObjectName("pageInit")
        self.verticalLayout_13.setObjectName("verticalLayout_13")
        self.verticalLayout_12.setObjectName("verticalLayout_12")

    def _build_init_header(self) -> None:
        """Создает заголовочную панель страницы инициализации."""
        self.horizontalLayout_17 = QtWidgets.QHBoxLayout()
        self.horizontalLayout_17.setSpacing(10)
        self.horizontalLayout_17.setObjectName("horizontalLayout_17")

        button_font = QtGui.QFont()
        button_font.setPointSize(10)

        self.btnInitNewTest = self._create_init_header_button(
            parent=self.pageInit,
            object_name="btnInitNewTest",
            font=button_font,
        )
        self.btnInitEdit = self._create_init_header_button(
            parent=self.pageInit,
            object_name="btnInitEdit",
            font=button_font,
        )
        self.btnInitSave = self._create_init_header_button(
            parent=self.pageInit,
            object_name="btnInitSave",
            font=button_font,
        )

        spacer = QtWidgets.QSpacerItem(
            40,
            20,
            QtWidgets.QSizePolicy.Policy.Expanding,
            QtWidgets.QSizePolicy.Policy.Minimum,
        )

        self.horizontalLayout_17.addWidget(self.btnInitNewTest)
        self.horizontalLayout_17.addWidget(self.btnInitEdit)
        self.horizontalLayout_17.addWidget(self.btnInitSave)
        self.horizontalLayout_17.addItem(spacer)
        self.verticalLayout_12.addLayout(self.horizontalLayout_17)

    def _create_init_header_button(
        self,
        *,
        parent: QtWidgets.QWidget,
        object_name: str,
        font: QtGui.QFont,
        width: int = 260,
    ) -> QtWidgets.QPushButton:
        """Создает кнопку заголовочной панели страницы инициализации."""

        button = QtWidgets.QPushButton(parent=parent)
        size_policy = QtWidgets.QSizePolicy(
            QtWidgets.QSizePolicy.Policy.Fixed,
            QtWidgets.QSizePolicy.Policy.Fixed,
        )
        button.setSizePolicy(size_policy)
        button.setMinimumSize(QtCore.QSize(width, 42))
        button.setMaximumSize(QtCore.QSize(width, 42))
        button.setFont(font)
        button.setObjectName(object_name)
        return button

    def _build_init_content(self) -> None:
        """Формирует основное содержимое страницы инициализации."""
        self.horizontalLayout_3 = QtWidgets.QHBoxLayout()
        self.horizontalLayout_3.setObjectName("horizontalLayout_3")

        self._build_init_info_column()
        self._build_init_placeholder_panel()

        self.horizontalLayout_3.addLayout(self.verticalLayout_11)
        self.horizontalLayout_3.addWidget(self.widget_2)
        self.horizontalLayout_3.setStretch(0, 8)
        self.horizontalLayout_3.setStretch(1, 1)

        self.verticalLayout_12.addLayout(self.horizontalLayout_3)
        self.verticalLayout_12.setStretch(0, 1)
        self.verticalLayout_12.setStretch(1, 8)
        self.verticalLayout_13.addLayout(self.verticalLayout_12)

    def _build_init_info_column(self) -> None:
        """Создает колонку с группами данных об испытании."""
        self.verticalLayout_11 = QtWidgets.QVBoxLayout()
        self.verticalLayout_11.setObjectName("verticalLayout_11")

        self._build_init_main_info_group()
        self._build_init_sample_info_group()
        self._build_init_test_info_group()

        spacer = QtWidgets.QSpacerItem(
            20,
            40,
            QtWidgets.QSizePolicy.Policy.Minimum,
            QtWidgets.QSizePolicy.Policy.Expanding,
        )
        self.verticalLayout_11.addItem(spacer)
        self.verticalLayout_11.setStretch(0, 4)
        self.verticalLayout_11.setStretch(1, 4)
        self.verticalLayout_11.setStretch(2, 4)
        self.verticalLayout_11.setStretch(3, 1)

    def _build_init_main_info_group(self) -> None:
        """Формирует блок "Основная информация"."""
        self.groupBox_4, form_layout = self._create_form_groupbox(
            parent=self.pageInit,
            object_name="groupBox_4",
            layout_name="formLayout",
        )
        field_pairs = [
            ("lineEdit", "label", True, True),
            ("lineEdit_2", "label_9", False, False),
            ("lineEdit_3", "label_10", False, False),
            ("lineEdit_4", "label_11", False, False),
            ("lineEdit_5", "label_12", False, False),
            ("lineEdit_11", "label_18", False, False),
            ("lineEdit_12", "label_19", False, False),
            ("lineEdit_13", "label_20", False, False),
        ]

        for row, (edit_name, label_name, align_left, label_min) in enumerate(field_pairs):
            self._add_line_edit_label_row(
                parent=self.groupBox_4,
                layout=form_layout,
                row=row,
                line_edit_name=edit_name,
                label_name=label_name,
                align_left=align_left,
                label_min=label_min,
            )

        self.verticalLayout_11.addWidget(self.groupBox_4)

    def _build_init_sample_info_group(self) -> None:
        """Формирует блок "Сведения об образце"."""
        self.groupBox_5, form_layout = self._create_form_groupbox(
            parent=self.pageInit,
            object_name="groupBox_5",
            layout_name="formLayout_2",
        )
        field_pairs = [
            ("lineEdit_6", "label_17", True, True),
            ("lineEdit_7", "label_13", False, False),
            ("lineEdit_8", "label_14", False, False),
            ("lineEdit_9", "label_15", False, False),
            ("lineEdit_10", "label_16", False, False),
        ]
        for row, (edit_name, label_name, align_left, label_min) in enumerate(field_pairs):
            self._add_line_edit_label_row(
                parent=self.groupBox_5,
                layout=form_layout,
                row=row,
                line_edit_name=edit_name,
                label_name=label_name,
                align_left=align_left,
                label_min=label_min,
            )
        self._add_sample_reuse_checkbox(form_layout, len(field_pairs))
        self.verticalLayout_11.addWidget(self.groupBox_5)

    def _build_init_test_info_group(self) -> None:
        """Формирует блок "Информация по испытанию"."""
        self.groupBox_6, form_layout = self._create_form_groupbox(
            parent=self.pageInit,
            object_name="groupBox_6",
            layout_name="formLayout_3",
        )

        list_pairs = [
            ("listWidget", "label_25"),
            ("listWidget_2", "label_26"),
            ("listWidget_3", "label_27"),
        ]

        for row, (list_name, label_name) in enumerate(list_pairs):
            self._add_list_label_row(
                parent=self.groupBox_6,
                layout=form_layout,
                row=row,
                list_name=list_name,
                label_name=label_name,
            )

        self.verticalLayout_11.addWidget(self.groupBox_6)

    def _build_init_placeholder_panel(self) -> None:
        """Создает правый заполнитель на странице инициализации."""
        self.widget_2 = QtWidgets.QWidget(parent=self.pageInit)
        self.widget_2.setObjectName("widget_2")

    def _create_static1_page(self) -> None:
        """Создает страницу "Статика 1"."""
        self.pageStatic1 = QtWidgets.QWidget()
        self.horizontalLayout_5 = QtWidgets.QHBoxLayout(self.pageStatic1)
        self.label_3 = QtWidgets.QLabel(parent=self.pageStatic1)

        self.pageStatic1.setObjectName("pageStatic1")
        self.horizontalLayout_5.setObjectName("horizontalLayout_5")
        font = QtGui.QFont()
        font.setPointSize(24)
        self.label_3.setFont(font)
        self.label_3.setAlignment(QtCore.Qt.AlignmentFlag.AlignCenter)
        self.label_3.setObjectName("label_3")

        self.horizontalLayout_5.addWidget(self.label_3)
        self.pager.addWidget(self.pageStatic1)

    def _create_static2_page(self) -> None:
        """Создает страницу "Статика 2"."""
        self.pageStatic2 = QtWidgets.QWidget()
        self.horizontalLayout_6 = QtWidgets.QHBoxLayout(self.pageStatic2)
        self.label_4 = QtWidgets.QLabel(parent=self.pageStatic2)

        self.pageStatic2.setObjectName("pageStatic2")
        self.horizontalLayout_6.setObjectName("horizontalLayout_6")
        font = QtGui.QFont()
        font.setPointSize(24)
        self.label_4.setFont(font)
        self.label_4.setAlignment(QtCore.Qt.AlignmentFlag.AlignCenter)
        self.label_4.setObjectName("label_4")

        self.horizontalLayout_6.addWidget(self.label_4)
        self.pager.addWidget(self.pageStatic2)

    def _create_calibration_page(self) -> None:
        """Создает страницу калибровки датчиков."""
        self.pageCalibration = QtWidgets.QWidget()
        self.horizontalLayout_calib = QtWidgets.QHBoxLayout(self.pageCalibration)
        self.label_calib = QtWidgets.QLabel(parent=self.pageCalibration)

        self.pageCalibration.setObjectName("pageCalibration")
        self.horizontalLayout_calib.setObjectName("horizontalLayout_calib")
        font = QtGui.QFont()
        font.setPointSize(24)
        self.label_calib.setFont(font)
        self.label_calib.setAlignment(QtCore.Qt.AlignmentFlag.AlignCenter)
        self.label_calib.setObjectName("label_calib")

        self.horizontalLayout_calib.addWidget(self.label_calib)
        self.pager.addWidget(self.pageCalibration)

    def _create_protocol_page(self) -> None:
        """Создает страницу протокола испытаний."""
        self.pageProtocol = QtWidgets.QWidget()
        self.horizontalLayout_protocol = QtWidgets.QHBoxLayout(self.pageProtocol)
        self.label_protocol = QtWidgets.QLabel(parent=self.pageProtocol)

        self.pageProtocol.setObjectName("pageProtocol")
        self.horizontalLayout_protocol.setObjectName("horizontalLayout_protocol")
        font = QtGui.QFont()
        font.setPointSize(24)
        self.label_protocol.setFont(font)
        self.label_protocol.setAlignment(QtCore.Qt.AlignmentFlag.AlignCenter)
        self.label_protocol.setObjectName("label_protocol")

        self.horizontalLayout_protocol.addWidget(self.label_protocol)
        self.pager.addWidget(self.pageProtocol)

    def _create_archive_page(self) -> None:
        """Создает страницу архива испытаний."""
        self.pageArchive = QtWidgets.QWidget()
        self.horizontalLayout_archive = QtWidgets.QHBoxLayout(self.pageArchive)
        self.label_archive = QtWidgets.QLabel(parent=self.pageArchive)

        self.pageArchive.setObjectName("pageArchive")
        self.horizontalLayout_archive.setObjectName("horizontalLayout_archive")
        font = QtGui.QFont()
        font.setPointSize(24)
        self.label_archive.setFont(font)
        self.label_archive.setAlignment(QtCore.Qt.AlignmentFlag.AlignCenter)
        self.label_archive.setObjectName("label_archive")

        self.horizontalLayout_archive.addWidget(self.label_archive)
        self.pager.addWidget(self.pageArchive)

    def _create_service_page(self) -> None:
        """Создает страницу сервисных операций."""
        self.pageService = QtWidgets.QWidget()
        self.horizontalLayout_4 = QtWidgets.QHBoxLayout(self.pageService)
        self.label_2 = QtWidgets.QLabel(parent=self.pageService)

        self.pageService.setObjectName("pageService")
        self.horizontalLayout_4.setObjectName("horizontalLayout_4")
        font = QtGui.QFont()
        font.setPointSize(24)
        self.label_2.setFont(font)
        self.label_2.setAlignment(QtCore.Qt.AlignmentFlag.AlignCenter)
        self.label_2.setObjectName("label_2")

        self.horizontalLayout_4.addWidget(self.label_2)
        self.pager.addWidget(self.pageService)

    def _finalize_main_layout(self, main_window: QtWidgets.QMainWindow) -> None:
        """Завершает сборку основного окна."""
        self.horizontalLayout.setStretch(0, 2)
        self.horizontalLayout.setStretch(1, 14)
        main_window.setCentralWidget(self.centralwidget)

    def _create_menu_bar(self, main_window: QtWidgets.QMainWindow) -> None:
        """Создает строку меню и строку состояния."""
        self.menubar = QtWidgets.QMenuBar(parent=main_window)
        self.menubar.setGeometry(QtCore.QRect(0, 0, 1743, 22))
        self.menubar.setObjectName("menubar")

        self.menuAbout = QtWidgets.QMenu(parent=self.menubar)
        self.menuAbout.setObjectName("menuAbout")
        self.menuExit = QtWidgets.QMenu(parent=self.menubar)
        self.menuExit.setObjectName("menuExit")
        self.menu = QtWidgets.QMenu(parent=self.menubar)
        self.menu.setObjectName("menu")

        main_window.setMenuBar(self.menubar)

        self.statusbar = QtWidgets.QStatusBar(parent=main_window)
        self.statusbar.setObjectName("statusbar")
        main_window.setStatusBar(self.statusbar)

        self.actionAbout = QtGui.QAction(parent=main_window)
        self.actionAbout.setObjectName("actionAbout")
        self.menuAbout.addAction(self.actionAbout)
        self.menubar.addAction(self.menuExit.menuAction())
        self.menubar.addAction(self.menu.menuAction())
        self.menubar.addAction(self.menuAbout.menuAction())

    def _connect_signals(self, main_window: QtWidgets.QMainWindow) -> None:
        """Подключает сигналы виджетов к обработчикам."""
        self.sldHandVelocity_1.valueChanged["int"].connect(self.dsbHandVelocity_1.update)
        self.sldHandTension.valueChanged["int"].connect(self.dsbHandTension.update)
        self.sldHandVelocity_2.valueChanged["int"].connect(self.dsbHandVelocity_2.update)
        QtCore.QMetaObject.connectSlotsByName(main_window)

    def _create_form_groupbox(
        self,
        *,
        parent: QtWidgets.QWidget,
        object_name: str,
        layout_name: str,
    ) -> tuple[QtWidgets.QGroupBox, QtWidgets.QFormLayout]:
        """Создает группу с формой и возвращает ее вместе с макетом."""
        group_box = QtWidgets.QGroupBox(parent=parent)
        group_box.setObjectName(object_name)
        font = QtGui.QFont()
        font.setPointSize(10)
        group_box.setFont(font)

        layout = QtWidgets.QFormLayout(group_box)
        layout.setFieldGrowthPolicy(
            QtWidgets.QFormLayout.FieldGrowthPolicy.AllNonFixedFieldsGrow
        )
        layout.setContentsMargins(10, 10, 10, 10)
        layout.setObjectName(layout_name)
        return group_box, layout

    def _add_line_edit_label_row(
        self,
        *,
        parent: QtWidgets.QWidget,
        layout: QtWidgets.QFormLayout,
        row: int,
        line_edit_name: str,
        label_name: str,
        align_left: bool,
        label_min: bool,
    ) -> None:
        """Добавляет в форму строку с полем ввода и подписью."""
        line_edit = QtWidgets.QLineEdit(parent=parent)
        label = QtWidgets.QLabel(parent=parent)
        setattr(self, line_edit_name, line_edit)
        setattr(self, label_name, label)

        self._configure_form_line_edit(line_edit, line_edit_name, align_left=align_left)
        self._configure_form_label(label, label_name, with_min_size=label_min)

        layout.setWidget(row, QtWidgets.QFormLayout.ItemRole.LabelRole, line_edit)
        layout.setWidget(row, QtWidgets.QFormLayout.ItemRole.FieldRole, label)

    def _add_list_label_row(
        self,
        *,
        parent: QtWidgets.QWidget,
        layout: QtWidgets.QFormLayout,
        row: int,
        list_name: str,
        label_name: str,
    ) -> None:
        """Добавляет в форму строку со списком и подписью."""
        list_widget = QtWidgets.QListWidget(parent=parent)
        label = QtWidgets.QLabel(parent=parent)
        setattr(self, list_name, list_widget)
        setattr(self, label_name, label)

        self._configure_form_list_widget(list_widget, list_name)
        self._configure_form_label(label, label_name, with_min_size=True)

        layout.setWidget(row, QtWidgets.QFormLayout.ItemRole.LabelRole, list_widget)
        layout.setWidget(row, QtWidgets.QFormLayout.ItemRole.FieldRole, label)

    def _add_sample_reuse_checkbox(
        self,
        layout: QtWidgets.QFormLayout,
        row: int,
    ) -> None:
        """Добавляет на форму чекбокс повторного использования образца."""
        self.checkBox = QtWidgets.QCheckBox(parent=self.groupBox_5)
        self.checkBox.setObjectName("checkBox")
        layout.setWidget(row, QtWidgets.QFormLayout.ItemRole.FieldRole, self.checkBox)

    @staticmethod
    def _configure_form_line_edit(
        line_edit: QtWidgets.QLineEdit,
        object_name: str,
        *,
        align_left: bool = False,
    ) -> None:
        """Настраивает параметры текстовых полей форм."""
        size_policy = QtWidgets.QSizePolicy(
            QtWidgets.QSizePolicy.Policy.Minimum,
            QtWidgets.QSizePolicy.Policy.Fixed,
        )
        size_policy.setHeightForWidth(line_edit.sizePolicy().hasHeightForWidth())
        line_edit.setSizePolicy(size_policy)
        line_edit.setMinimumSize(QtCore.QSize(300, 0))
        font = QtGui.QFont()
        font.setPointSize(10)
        line_edit.setFont(font)
        if align_left:
            line_edit.setAlignment(
                QtCore.Qt.AlignmentFlag.AlignLeading
                | QtCore.Qt.AlignmentFlag.AlignLeft
                | QtCore.Qt.AlignmentFlag.AlignVCenter
            )
        line_edit.setObjectName(object_name)

    @staticmethod
    def _configure_form_label(
        label: QtWidgets.QLabel,
        object_name: str,
        *,
        with_min_size: bool = False,
    ) -> None:
        """Настраивает параметры подписей в формах."""
        font = QtGui.QFont()
        font.setPointSize(10)
        label.setFont(font)
        if with_min_size:
            label.setMinimumSize(QtCore.QSize(0, 0))
        label.setObjectName(object_name)

    @staticmethod
    def _configure_form_list_widget(
        list_widget: QtWidgets.QListWidget,
        object_name: str,
    ) -> None:
        """Настраивает список выбора в форме."""
        size_policy = QtWidgets.QSizePolicy(
            QtWidgets.QSizePolicy.Policy.Minimum,
            QtWidgets.QSizePolicy.Policy.Maximum,
        )
        size_policy.setHeightForWidth(list_widget.sizePolicy().hasHeightForWidth())
        list_widget.setSizePolicy(size_policy)
        list_widget.setMinimumSize(QtCore.QSize(300, 0))
        list_widget.setMaximumHeight(25)
        font = QtGui.QFont()
        font.setPointSize(10)
        list_widget.setFont(font)
        list_widget.setObjectName(object_name)

    def retranslate_ui(self, MainWindow: QtWidgets.QMainWindow) -> None:
        """Назначает текстовые подписи элементов интерфейса."""
        _translate = QtCore.QCoreApplication.translate
        MainWindow.setWindowTitle(_translate("MainWindow", "Повортная статика"))
        self._retranslate_left_panel(_translate)
        self._retranslate_hand_section(_translate)
        self._retranslate_init_controls(_translate)
        self._retranslate_init_main_info(_translate)
        self._retranslate_init_sample_info(_translate)
        self._retranslate_init_test_info(_translate)
        self._retranslate_placeholder_pages(_translate)
        self._retranslate_menu(_translate)

    def _retranslate_left_panel(self, translate) -> None:
        self.btnInit.setText(translate("MainWindow", "Инициализация испытания"))
        self.btnStatic1.setText(translate("MainWindow", "Статика 1"))
        self.btnStatic2.setText(translate("MainWindow", "Статика 2"))
        self.btnHand.setText(translate("MainWindow", "Ручное управление"))
        self.btnCalibration.setText(translate("MainWindow", "Калибровка датчиков"))
        self.btnProtocol.setText(translate("MainWindow", "Протокол/Результаты"))
        self.btnArchive.setText(translate("MainWindow", "Архив"))
        self.btnService.setText(translate("MainWindow", "Сервис"))
        self.btnStart.setText(translate("MainWindow", "Запуск"))
        self.btnPause.setText(translate("MainWindow", "Пауза/Продолжить"))
        self.btnStop.setText(translate("MainWindow", "Стоп"))
        self.btnEmergencyReset.setText(translate("MainWindow", "Сброс аварии"))

    def _retranslate_hand_section(self, translate) -> None:
        self.groupBox_3.setTitle(translate("MainWindow", "Сервопривод"))
        self.btnServoPower.setText(translate("MainWindow", "Сервопривод ВКЛ"))
        self.groupBox.setTitle(translate("MainWindow", "Ручное управление сервоприводом"))
        self.label_5.setText(translate("MainWindow", "Угловая скорость:"))
        self.dsbHandVelocity_1.setSuffix(translate("MainWindow", "°/мин"))
        self.btnJog_CCW.setText(translate("MainWindow", "Против часовой"))
        self.btnJog_CW.setText(translate("MainWindow", "По часовой"))
        self.groupBox_2.setTitle(translate("MainWindow", "Управление статическим моментом"))
        self.label_6.setText(translate("MainWindow", "Момент:"))
        self.dsbHandTension.setSuffix(translate("MainWindow", " Нм"))
        self.label_7.setText(translate("MainWindow", "Скорость нарастания:"))
        self.dsbHandVelocity_2.setSuffix(translate("MainWindow", " Нм/с"))
        self.label_8.setText(translate("MainWindow", "Время выдержки:"))
        self.dsbHandTime_1.setSuffix(translate("MainWindow", " с"))
        self.pushButton_2.setText(translate("MainWindow", "Пуск"))
        self.btnHandRegSettings.setText(translate("MainWindow", "..."))
        self.toolButton_2.setText(translate("MainWindow", "..."))

    def _retranslate_init_controls(self, translate) -> None:
        self.btnInitNewTest.setText(
            translate("MainWindow", "Новое испытание")
        )
        self.btnInitEdit.setText(translate("MainWindow", "Редактировать"))
        self.btnInitSave.setText(
            translate("MainWindow", "Сохранить данные испытания")
        )

    def _retranslate_init_main_info(self, translate) -> None:
        self.groupBox_4.setTitle(translate("MainWindow", "Основная информация"))
        self.label.setText(translate("MainWindow", "Номер протокола испытаний"))
        self.label_9.setText(translate("MainWindow", "Наименование и адрес испытательной лаборатории"))
        self.label_10.setText(translate("MainWindow", "Наименование поставщика образцов"))
        self.label_11.setText(translate("MainWindow", "Наименование изготовителя"))
        self.label_12.setText(translate("MainWindow", "Номер ПМ"))
        self.label_18.setText(translate("MainWindow", "Марка и модель стенда"))
        self.label_19.setText(translate("MainWindow", "Серийный номер стенда"))
        self.label_20.setText(translate("MainWindow", "Дата аттестации стенда"))

    def _retranslate_init_sample_info(self, translate) -> None:
        self.groupBox_5.setTitle(translate("MainWindow", "Сведения об исследуемом образце"))
        self.label_13.setText(translate("MainWindow", "Дата получения образца на испытание"))
        self.label_14.setText(
            translate(
                "MainWindow",
                "Документ, подтверждающий отбор образцов из серийной продукции",
            )
        )
        self.label_15.setText(translate("MainWindow", "Дата проведения испытания"))
        self.label_16.setText(
            translate(
                "MainWindow",
                "Номер предыдущего протокола (при повторном использовании)",
            )
        )
        self.label_17.setText(translate("MainWindow", "Полностью отслеживаемое обозначение образца"))
        self.checkBox.setText(translate("MainWindow", "Образец используется повторно"))

    def _retranslate_init_test_info(self, translate) -> None:
        self.groupBox_6.setTitle(translate("MainWindow", "Информация по испытанию"))
        self.label_25.setText(translate("MainWindow", "Вид испытания"))
        self.label_26.setText(translate("MainWindow", "Применение образца"))
        self.label_27.setText(translate("MainWindow", "Уровень нагружения"))

    def _retranslate_placeholder_pages(self, translate) -> None:
        self.label_3.setText(translate("MainWindow", "Статика 1"))
        self.label_4.setText(translate("MainWindow", "Статика 2"))
        self.label_calib.setText(translate("MainWindow", "Калибровка датчиков"))
        self.label_protocol.setText(translate("MainWindow", "Протокол/Результаты"))
        self.label_archive.setText(translate("MainWindow", "Архив"))
        self.label_2.setText(translate("MainWindow", "Сервис"))

    def _retranslate_menu(self, translate) -> None:
        self.menuAbout.setTitle(translate("MainWindow", "О программе"))
        self.menuExit.setTitle(translate("MainWindow", "Выход"))
        self.menu.setTitle(translate("MainWindow", "Настройки"))
        self.actionAbout.setText(translate("MainWindow", "О программе"))
