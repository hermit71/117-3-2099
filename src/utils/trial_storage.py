"""Хранилище данных инициализации испытаний."""

from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime
from pathlib import Path
from typing import Optional

import sqlite3


def _text(row: sqlite3.Row, key: str) -> str:
    """Вернуть строковое значение поля, заменяя ``None`` на пустую строку."""

    value = row[key]
    return "" if value is None else str(value)


@dataclass
class TrialInitRecord:
    """Строка таблицы trials__init_data."""

    id: Optional[int] = None
    trial_number: str = ""
    stand_number: str = ""
    test_type_code: int = 1
    test_type: str = ""
    protocol_number: str = ""
    lab_address: str = ""
    sample_supplier: str = ""
    manufacturer: str = ""
    pm_number: str = ""
    stand_brand: str = ""
    stand_serial: str = ""
    stand_certification_date: str = ""
    sample_designation: str = ""
    sample_receipt_date: str = ""
    selection_document: str = ""
    test_date: str = ""
    previous_protocol_number: str = ""
    sample_reused: bool = False
    sample_application: str = ""
    load_level: str = ""
    sequence_index: int = 0
    created_at: str = ""
    updated_at: str = ""

    def to_db_dict(self) -> dict[str, object]:
        """Преобразовать запись в словарь для sqlite."""

        return {
            "id": self.id,
            "trial_number": self.trial_number,
            "stand_number": self.stand_number,
            "test_type_code": self.test_type_code,
            "test_type": self.test_type,
            "protocol_number": self.protocol_number,
            "lab_address": self.lab_address,
            "sample_supplier": self.sample_supplier,
            "manufacturer": self.manufacturer,
            "pm_number": self.pm_number,
            "stand_brand": self.stand_brand,
            "stand_serial": self.stand_serial,
            "stand_certification_date": self.stand_certification_date,
            "sample_designation": self.sample_designation,
            "sample_receipt_date": self.sample_receipt_date,
            "selection_document": self.selection_document,
            "test_date": self.test_date,
            "previous_protocol_number": self.previous_protocol_number,
            "sample_reused": int(self.sample_reused),
            "sample_application": self.sample_application,
            "load_level": self.load_level,
            "sequence_index": self.sequence_index,
            "created_at": self.created_at,
            "updated_at": self.updated_at,
        }

    @classmethod
    def from_row(cls, row: sqlite3.Row) -> "TrialInitRecord":
        """Создать запись из строки базы данных."""

        return cls(
            id=row["id"],
            trial_number=_text(row, "trial_number"),
            stand_number=_text(row, "stand_number"),
            test_type_code=row["test_type_code"],
            test_type=_text(row, "test_type"),
            protocol_number=_text(row, "protocol_number"),
            lab_address=_text(row, "lab_address"),
            sample_supplier=_text(row, "sample_supplier"),
            manufacturer=_text(row, "manufacturer"),
            pm_number=_text(row, "pm_number"),
            stand_brand=_text(row, "stand_brand"),
            stand_serial=_text(row, "stand_serial"),
            stand_certification_date=_text(row, "stand_certification_date"),
            sample_designation=_text(row, "sample_designation"),
            sample_receipt_date=_text(row, "sample_receipt_date"),
            selection_document=_text(row, "selection_document"),
            test_date=_text(row, "test_date"),
            previous_protocol_number=_text(row, "previous_protocol_number"),
            sample_reused=bool(row["sample_reused"]),
            sample_application=_text(row, "sample_application"),
            load_level=_text(row, "load_level"),
            sequence_index=row["sequence_index"],
            created_at=_text(row, "created_at"),
            updated_at=_text(row, "updated_at"),
        )


class TrialStorage:
    """Обёртка над sqlite для хранения данных испытаний."""

    def __init__(self, db_path: Path | str):
        self.db_path = Path(db_path)
        self._ensure_schema()

    def _connect(self) -> sqlite3.Connection:
        """Создать соединение с установкой row_factory."""

        self.db_path.parent.mkdir(parents=True, exist_ok=True)
        conn = sqlite3.connect(self.db_path)
        conn.row_factory = sqlite3.Row
        return conn

    def _ensure_schema(self) -> None:
        """Создать таблицу trials__init_data при необходимости."""

        with self._connect() as conn:
            conn.execute(
                """
                CREATE TABLE IF NOT EXISTS trials__init_data (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    trial_number TEXT NOT NULL UNIQUE,
                    stand_number TEXT NOT NULL,
                    test_type_code INTEGER NOT NULL,
                    test_type TEXT NOT NULL,
                    protocol_number TEXT,
                    lab_address TEXT,
                    sample_supplier TEXT,
                    manufacturer TEXT,
                    pm_number TEXT,
                    stand_brand TEXT,
                    stand_serial TEXT,
                    stand_certification_date TEXT,
                    sample_designation TEXT,
                    sample_receipt_date TEXT,
                    selection_document TEXT,
                    test_date TEXT,
                    previous_protocol_number TEXT,
                    sample_reused INTEGER NOT NULL,
                    sample_application TEXT,
                    load_level TEXT,
                    sequence_index INTEGER NOT NULL UNIQUE,
                    created_at TEXT NOT NULL,
                    updated_at TEXT NOT NULL
                )
                """
            )

    @staticmethod
    def build_trial_number(stand_number: str, test_type_code: int, sequence: int) -> str:
        """Сформировать номер испытания по шаблону X-Y-Z."""

        stand = stand_number.strip() or "000"
        return f"{stand}-{test_type_code}-{sequence:06d}"

    def get_next_sequence(self) -> int:
        """Вернуть следующий порядковый номер испытания."""

        with self._connect() as conn:
            cursor = conn.execute(
                "SELECT MAX(sequence_index) FROM trials__init_data"
            )
            result = cursor.fetchone()[0]
        return 1 if result is None else int(result) + 1

    def save_trial(self, record: TrialInitRecord) -> TrialInitRecord:
        """Добавить или обновить запись испытания."""

        if record.id is None:
            return self._insert_trial(record)
        return self._update_trial(record)

    def _insert_trial(self, record: TrialInitRecord) -> TrialInitRecord:
        """Создать новую запись испытания."""

        now = datetime.utcnow().isoformat()
        record.created_at = now
        record.updated_at = now
        if not record.trial_number:
            record.trial_number = self.build_trial_number(
                record.stand_number, record.test_type_code, record.sequence_index
            )
        with self._connect() as conn:
            cursor = conn.execute(
                """
                INSERT INTO trials__init_data (
                    trial_number, stand_number, test_type_code, test_type,
                    protocol_number, lab_address, sample_supplier, manufacturer,
                    pm_number, stand_brand, stand_serial, stand_certification_date,
                    sample_designation, sample_receipt_date, selection_document,
                    test_date, previous_protocol_number, sample_reused,
                    sample_application, load_level, sequence_index,
                    created_at, updated_at
                ) VALUES (
                    :trial_number, :stand_number, :test_type_code, :test_type,
                    :protocol_number, :lab_address, :sample_supplier, :manufacturer,
                    :pm_number, :stand_brand, :stand_serial, :stand_certification_date,
                    :sample_designation, :sample_receipt_date, :selection_document,
                    :test_date, :previous_protocol_number, :sample_reused,
                    :sample_application, :load_level, :sequence_index,
                    :created_at, :updated_at
                )
                """,
                record.to_db_dict(),
            )
            record.id = cursor.lastrowid
        return record

    def _update_trial(self, record: TrialInitRecord) -> TrialInitRecord:
        """Обновить существующую запись."""

        record.updated_at = datetime.utcnow().isoformat()
        with self._connect() as conn:
            conn.execute(
                """
                UPDATE trials__init_data SET
                    trial_number=:trial_number,
                    stand_number=:stand_number,
                    test_type_code=:test_type_code,
                    test_type=:test_type,
                    protocol_number=:protocol_number,
                    lab_address=:lab_address,
                    sample_supplier=:sample_supplier,
                    manufacturer=:manufacturer,
                    pm_number=:pm_number,
                    stand_brand=:stand_brand,
                    stand_serial=:stand_serial,
                    stand_certification_date=:stand_certification_date,
                    sample_designation=:sample_designation,
                    sample_receipt_date=:sample_receipt_date,
                    selection_document=:selection_document,
                    test_date=:test_date,
                    previous_protocol_number=:previous_protocol_number,
                    sample_reused=:sample_reused,
                    sample_application=:sample_application,
                    load_level=:load_level,
                    sequence_index=:sequence_index,
                    updated_at=:updated_at
                WHERE id=:id
                """,
                record.to_db_dict(),
            )
        return record

    def get_last_trial(self) -> Optional[TrialInitRecord]:
        """Получить последнюю сохранённую запись."""

        with self._connect() as conn:
            cursor = conn.execute(
                "SELECT * FROM trials__init_data ORDER BY id DESC LIMIT 1"
            )
            row = cursor.fetchone()
        return None if row is None else TrialInitRecord.from_row(row)
