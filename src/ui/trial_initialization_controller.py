"""Логика экрана инициализации испытания."""

from __future__ import annotations

import sqlite3
from pathlib import Path
from typing import Dict, List, Optional, Tuple, TYPE_CHECKING

from PyQt6.QtCore import QDate
from PyQt6.QtWidgets import (
    QComboBox,
    QDateEdit,
    QFormLayout,
    QLabel,
    QLineEdit,
    QMessageBox,
    QPushButton,
    QWidget,
)

from src.utils.config import Config
from src.utils.stand_mode import StandMode, StandState
from src.utils.trial_storage import TrialInitRecord, TrialStorage

if TYPE_CHECKING:
    from src.ui.main_window import MainWindow


class TrialInitializationController:
    """Управляет состоянием и сохранением данных инициализации."""

    TEST_TYPES: List[Tuple[str, int]] = [
        ("Статическое проверочное испытание на кручение", 1),
        ("Дополнительное статическое испытание на кручение", 2),
    ]

    DATE_DISPLAY_FORMAT = "dd.MM.yyyy"

    def __init__(self, window: "MainWindow", config: Config):
        self.window = window
        self.config = config
        db_path = Path(__file__).resolve().parents[2] / "config" / "trials.sqlite3"
        self.storage = TrialStorage(db_path)
        self.current_trial: Optional[TrialInitRecord] = None
        self._pending_sequence: Optional[int] = None
        self._is_edit_mode = False

        self.btn_new_trial: QPushButton = self.window.pushButton
        self.btn_save_trial: QPushButton = self.window.pushButton_3
        self.btn_edit_trial = QPushButton("Редактировать", parent=self.window.pageInit)

        self.trial_number_field: Optional[QLineEdit] = None
        self.test_type_combo: Optional[QComboBox] = None
        self.sample_application_field: Optional[QLineEdit] = None
        self.load_level_field: Optional[QLineEdit] = None

        self._text_fields: Dict[str, QLineEdit] = {}
        self._date_fields: Dict[str, QDateEdit] = {}

        self._setup_buttons()
        self._prepare_form()
        self._connect_signals()
        self._load_initial_state()

    # ------------------------------------------------------------------
    # Инициализация интерфейса
    # ------------------------------------------------------------------
    def _setup_buttons(self) -> None:
        """Настроить кнопки управления формой."""

        self.btn_save_trial.setText("Сохранить данные испытания")
        layout = self.window.horizontalLayout_17
        layout.insertWidget(1, self.btn_edit_trial)
        self.btn_edit_trial.setEnabled(False)

    def _prepare_form(self) -> None:
        """Подготовить и заменить необходимые виджеты формы."""

        self._create_trial_number_row()
        self._prepare_text_fields()
        self._prepare_date_fields()
        self._prepare_test_type_field()
        self._prepare_additional_fields()
        self._set_fields_enabled(False)

    def _create_trial_number_row(self) -> None:
        """Добавить строку с номером испытания."""

        form: QFormLayout = self.window.formLayout
        label = QLabel("Номер испытания", parent=self.window.widget1)
        label.setObjectName("label_trial_number")
        self.trial_number_field = QLineEdit(parent=self.window.widget1)
        self.trial_number_field.setObjectName("lineTrialNumber")
        self.trial_number_field.setReadOnly(True)
        self.trial_number_field.setMinimumSize(self.window.lineEdit.minimumSize())
        form.insertRow(0, label, self.trial_number_field)
        self.window.lineTrialNumber = self.trial_number_field

    def _prepare_text_fields(self) -> None:
        """Сохранить ссылки на текстовые поля формы."""

        self._text_fields = {
            "protocol_number": self.window.lineEdit,
            "lab_address": self.window.lineEdit_2,
            "sample_supplier": self.window.lineEdit_3,
            "manufacturer": self.window.lineEdit_4,
            "pm_number": self.window.lineEdit_5,
            "stand_brand": self.window.lineEdit_11,
            "stand_serial": self.window.lineEdit_12,
            "sample_designation": self.window.lineEdit_6,
            "selection_document": self.window.lineEdit_8,
            "previous_protocol_number": self.window.lineEdit_10,
        }

    def _prepare_date_fields(self) -> None:
        """Заменить поля даты на QDateEdit."""

        self._date_fields = {
            "stand_certification_date": self._replace_with_date_edit(
                self.window.formLayout, self.window.lineEdit_13, "dateStandCertification"
            ),
            "sample_receipt_date": self._replace_with_date_edit(
                self.window.formLayout_2, self.window.lineEdit_7, "dateSampleReceipt"
            ),
            "test_date": self._replace_with_date_edit(
                self.window.formLayout_2, self.window.lineEdit_9, "dateTest"
            ),
        }

    def _prepare_test_type_field(self) -> None:
        """Заменить список вида испытания на выпадающий список."""

        self.test_type_combo = QComboBox(parent=self.window.layoutWidget_2)
        self.test_type_combo.setObjectName("comboTestType")
        for text, _code in self.TEST_TYPES:
            self.test_type_combo.addItem(text)
        self._replace_form_widget(
            self.window.formLayout_3, self.window.listWidget, self.test_type_combo
        )
        self.window.comboTestType = self.test_type_combo
        self.window.listWidget = self.test_type_combo

    def _prepare_additional_fields(self) -> None:
        """Подготовить поля применения и уровня нагружения."""

        self.sample_application_field = QLineEdit(parent=self.window.layoutWidget_2)
        self.sample_application_field.setObjectName("lineSampleApplication")
        self.sample_application_field.setMinimumSize(self.window.lineEdit_6.minimumSize())
        self._replace_form_widget(
            self.window.formLayout_3,
            self.window.listWidget_2,
            self.sample_application_field,
        )
        self.window.lineSampleApplication = self.sample_application_field
        self.window.listWidget_2 = self.sample_application_field

        self.load_level_field = QLineEdit(parent=self.window.layoutWidget_2)
        self.load_level_field.setObjectName("lineLoadLevel")
        self.load_level_field.setMinimumSize(self.window.lineEdit_6.minimumSize())
        self._replace_form_widget(
            self.window.formLayout_3,
            self.window.listWidget_3,
            self.load_level_field,
        )
        self.window.lineLoadLevel = self.load_level_field
        self.window.listWidget_3 = self.load_level_field

    # ------------------------------------------------------------------
    # Работа с формой
    # ------------------------------------------------------------------
    def _replace_with_date_edit(
        self, layout: QFormLayout, old_widget: QLineEdit, object_name: str
    ) -> QDateEdit:
        """Заменить QLineEdit дат на QDateEdit."""

        date_edit = QDateEdit(parent=old_widget.parentWidget())
        date_edit.setObjectName(object_name)
        date_edit.setCalendarPopup(True)
        date_edit.setDisplayFormat(self.DATE_DISPLAY_FORMAT)
        date_edit.setDate(QDate.currentDate())
        self._replace_form_widget(layout, old_widget, date_edit)
        setattr(self.window, old_widget.objectName(), date_edit)
        return date_edit

    @staticmethod
    def _replace_form_widget(
        layout: QFormLayout, old_widget: QWidget, new_widget: QWidget
    ) -> None:
        """Заменить виджет в форме, сохранив позицию."""

        index = layout.indexOf(old_widget)
        if index == -1:
            return
        position = layout.getItemPosition(index)
        if len(position) == 2:
            row, role = position
        elif len(position) == 4:
            row, role, _, _ = position
        else:
            row, role = 0, QFormLayout.ItemRole.FieldRole
        layout.removeWidget(old_widget)
        old_widget.deleteLater()
        layout.setWidget(row, role, new_widget)

    def _connect_signals(self) -> None:
        """Подключить обработчики кнопок и полей."""

        self.btn_new_trial.clicked.connect(self._on_new_trial_clicked)
        self.btn_save_trial.clicked.connect(self._on_save_clicked)
        self.btn_edit_trial.clicked.connect(self._on_edit_clicked)
        if self.test_type_combo:
            self.test_type_combo.currentIndexChanged.connect(
                lambda _index: self._update_trial_number_display()
            )

    def _set_fields_enabled(self, enabled: bool) -> None:
        """Изменить доступность всех полей формы."""

        widgets: List[QWidget] = list(self._text_fields.values())
        widgets.extend(self._date_fields.values())
        widgets.append(self.window.checkBox)
        if self.test_type_combo:
            widgets.append(self.test_type_combo)
        if self.sample_application_field:
            widgets.append(self.sample_application_field)
        if self.load_level_field:
            widgets.append(self.load_level_field)
        for widget in widgets:
            widget.setEnabled(enabled)
        if self.trial_number_field:
            self.trial_number_field.setEnabled(True)
            self.trial_number_field.setReadOnly(True)

    # ------------------------------------------------------------------
    # Загрузка и отображение данных
    # ------------------------------------------------------------------
    def _load_initial_state(self) -> None:
        """Заполнить форму сохранёнными данными или значениями по умолчанию."""

        record = self.storage.get_last_trial()
        if record:
            self.current_trial = record
            self._pending_sequence = record.sequence_index
            self._fill_form_from_record(record)
            StandState.set_mode(StandMode.TESTING)
            self.btn_edit_trial.setEnabled(True)
            self.btn_save_trial.setEnabled(False)
            self._set_fields_enabled(False)
        else:
            StandState.set_mode(StandMode.PREPARATION)
            self._pending_sequence = None
            self._clear_form_for_new_trial()
            self.btn_edit_trial.setEnabled(False)
            self.btn_save_trial.setEnabled(False)

    def _fill_form_from_record(self, record: TrialInitRecord) -> None:
        """Отобразить данные записи в полях формы."""

        for key, field in self._text_fields.items():
            field.setText(getattr(record, key, ""))
        self.sample_application_field.setText(record.sample_application)
        self.load_level_field.setText(record.load_level)
        self.window.checkBox.setChecked(record.sample_reused)
        self._set_date_from_string(
            self._date_fields["stand_certification_date"],
            record.stand_certification_date,
        )
        self._set_date_from_string(
            self._date_fields["sample_receipt_date"],
            record.sample_receipt_date,
        )
        self._set_date_from_string(
            self._date_fields["test_date"],
            record.test_date,
        )
        if self.test_type_combo:
            index = self._test_type_index(record.test_type_code)
            self.test_type_combo.setCurrentIndex(index)
        if self.trial_number_field:
            self.trial_number_field.setText(record.trial_number)

    def _clear_form_for_new_trial(self) -> None:
        """Очистить поля и заполнить данными из конфигурации."""

        for field in self._text_fields.values():
            field.clear()
        self.sample_application_field.clear()
        self.load_level_field.clear()
        self.window.checkBox.setChecked(False)
        today = QDate.currentDate()
        for date_edit in self._date_fields.values():
            date_edit.setDate(today)
        self._apply_stand_defaults()
        self._update_trial_number_display()

    def _apply_stand_defaults(self) -> None:
        """Заполнить поля стенда из конфигурации."""

        if not self.config:
            return
        stand_defaults = {
            "lab_address": self.config.get("stand", "lab_address", ""),
            "stand_brand": self.config.get("stand", "brand_and_model", ""),
            "stand_serial": self.config.get("stand", "serial_number", ""),
        }
        for key, value in stand_defaults.items():
            self._text_fields[key].setText(value)
        date_value = self.config.get("stand", "certification_date", "")
        self._set_date_from_string(
            self._date_fields["stand_certification_date"],
            date_value,
        )

    # ------------------------------------------------------------------
    # Обработка событий
    # ------------------------------------------------------------------
    def _on_new_trial_clicked(self) -> None:
        """Перевести форму в режим ввода нового испытания."""

        StandState.set_mode(StandMode.PREPARATION)
        self.current_trial = None
        self._pending_sequence = self.storage.get_next_sequence()
        self._clear_form_for_new_trial()
        self._enter_edit_mode()

    def _on_edit_clicked(self) -> None:
        """Разрешить изменение сохранённых данных."""

        if not self.current_trial:
            return
        self._pending_sequence = self.current_trial.sequence_index
        self._enter_edit_mode()

    def _enter_edit_mode(self) -> None:
        """Активировать редактирование полей."""

        self._is_edit_mode = True
        self._set_fields_enabled(True)
        self.btn_save_trial.setEnabled(True)
        self.btn_edit_trial.setEnabled(False)
        self.btn_new_trial.setEnabled(False)

    def _leave_edit_mode(self) -> None:
        """Завершить редактирование."""

        self._is_edit_mode = False
        self._set_fields_enabled(False)
        self.btn_save_trial.setEnabled(False)
        self.btn_edit_trial.setEnabled(bool(self.current_trial))
        self.btn_new_trial.setEnabled(True)

    def _on_save_clicked(self) -> None:
        """Сохранить текущие данные формы."""

        if not self._is_edit_mode:
            return
        record = self._collect_form_data()
        try:
            saved = self.storage.save_trial(record)
        except sqlite3.IntegrityError as error:
            QMessageBox.warning(
                self.window,
                "Ошибка сохранения",
                f"Не удалось сохранить данные испытания: {error}",
            )
            return
        self.current_trial = saved
        self._pending_sequence = saved.sequence_index
        if self.trial_number_field:
            self.trial_number_field.setText(saved.trial_number)
        StandState.set_mode(StandMode.TESTING)
        self._leave_edit_mode()
        QMessageBox.information(
            self.window,
            "Сохранение",
            "Данные испытания сохранены.",
        )

    # ------------------------------------------------------------------
    # Сбор и преобразование данных
    # ------------------------------------------------------------------
    def _collect_form_data(self) -> TrialInitRecord:
        """Сформировать объект TrialInitRecord из полей формы."""

        sequence = self._determine_sequence()
        stand_number = self._text_fields["stand_serial"].text().strip() or "000"
        test_type_code = self._current_test_type_code()
        trial_number = self.storage.build_trial_number(
            stand_number, test_type_code, sequence
        )

        record = TrialInitRecord(
            id=self.current_trial.id if self.current_trial else None,
            trial_number=trial_number,
            stand_number=stand_number,
            test_type_code=test_type_code,
            test_type=self.test_type_combo.currentText() if self.test_type_combo else "",
            sequence_index=sequence,
        )
        for key, field in self._text_fields.items():
            setattr(record, key, field.text().strip())
        record.sample_application = (
            self.sample_application_field.text().strip() if self.sample_application_field else ""
        )
        record.load_level = (
            self.load_level_field.text().strip() if self.load_level_field else ""
        )
        record.sample_reused = self.window.checkBox.isChecked()
        record.stand_certification_date = self._iso_date(
            self._date_fields["stand_certification_date"],
        )
        record.sample_receipt_date = self._iso_date(
            self._date_fields["sample_receipt_date"],
        )
        record.test_date = self._iso_date(self._date_fields["test_date"])
        return record

    def _determine_sequence(self) -> int:
        """Определить порядковый номер испытания."""

        if self.current_trial:
            return self.current_trial.sequence_index
        if self._pending_sequence is None:
            self._pending_sequence = self.storage.get_next_sequence()
        return self._pending_sequence

    def _current_test_type_code(self) -> int:
        """Вернуть код выбранного вида испытания."""

        if not self.test_type_combo:
            return 1
        index = self.test_type_combo.currentIndex()
        return self.TEST_TYPES[index][1]

    # ------------------------------------------------------------------
    # Утилиты работы с датами и типами
    # ------------------------------------------------------------------
    def _set_date_from_string(self, widget: QDateEdit, value: str) -> None:
        """Заполнить виджет даты из строки."""

        if not value:
            widget.setDate(QDate.currentDate())
            return
        for pattern in ("yyyy-MM-dd", "dd.MM.yyyy", "dd.MM.yyyy г", "dd.MM.yyyy г."):
            date = QDate.fromString(value.strip(), pattern)
            if date.isValid():
                widget.setDate(date)
                return
        widget.setDate(QDate.currentDate())

    def _update_trial_number_display(self) -> None:
        """Обновить поле номера испытания."""

        if not self.trial_number_field:
            return
        sequence = self._determine_sequence()
        stand_number = self._text_fields["stand_serial"].text().strip() or "000"
        test_type_code = self._current_test_type_code()
        self.trial_number_field.setText(
            self.storage.build_trial_number(stand_number, test_type_code, sequence)
        )

    def _test_type_index(self, code: int) -> int:
        """Найти индекс кода испытания в списке."""

        for index, (_text, stored_code) in enumerate(self.TEST_TYPES):
            if stored_code == code:
                return index
        return 0

    @staticmethod
    def _iso_date(date_edit: QDateEdit) -> str:
        """Вернуть дату в формате ISO."""

        return date_edit.date().toString("yyyy-MM-dd")
