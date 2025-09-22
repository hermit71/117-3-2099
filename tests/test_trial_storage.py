"""Тесты для модуля trial_storage."""

from __future__ import annotations

import tempfile
import unittest
from pathlib import Path

from src.utils.trial_storage import TrialInitRecord, TrialStorage


class TrialStorageTestCase(unittest.TestCase):
    """Проверка основных сценариев работы хранилища испытаний."""

    def setUp(self) -> None:
        self._tmp_dir = tempfile.TemporaryDirectory()
        db_path = Path(self._tmp_dir.name) / "trials.sqlite3"
        self.storage = TrialStorage(db_path)

    def tearDown(self) -> None:
        self._tmp_dir.cleanup()

    def test_build_trial_number(self) -> None:
        """Номер испытания формируется по шаблону X-Y-Z."""

        number = TrialStorage.build_trial_number("123", 2, 7)
        self.assertEqual(number, "123-2-000007")

    def test_next_sequence_increments(self) -> None:
        """Следующий порядковый номер увеличивается после сохранения."""

        first = self.storage.get_next_sequence()
        record = self._create_record(sequence=first)
        self.storage.save_trial(record)
        next_sequence = self.storage.get_next_sequence()
        self.assertEqual(next_sequence, first + 1)

    def test_insert_and_update_trial(self) -> None:
        """Вставка создаёт запись, обновление сохраняет изменения."""

        record = self._create_record(sequence=self.storage.get_next_sequence())
        saved = self.storage.save_trial(record)
        self.assertIsNotNone(saved.id)
        self.assertTrue(saved.trial_number.endswith("000001"))

        saved.protocol_number = "PN-001"
        saved.lab_address = "Тестовая лаборатория"
        updated = self.storage.save_trial(saved)
        latest = self.storage.get_last_trial()
        self.assertEqual(updated.protocol_number, "PN-001")
        self.assertEqual(latest.protocol_number, "PN-001")
        self.assertEqual(latest.lab_address, "Тестовая лаборатория")

    def _create_record(self, sequence: int) -> TrialInitRecord:
        """Создать базовую запись для сохранения в БД."""

        return TrialInitRecord(
            stand_number="001",
            test_type_code=1,
            test_type="Статическое проверочное испытание на кручение",
            sequence_index=sequence,
            protocol_number="",
            lab_address="",
            sample_supplier="",
            manufacturer="",
            pm_number="",
            stand_brand="",
            stand_serial="001",
            stand_certification_date="2024-01-01",
            sample_designation="",
            sample_receipt_date="2024-01-02",
            selection_document="",
            test_date="2024-01-03",
            previous_protocol_number="",
            sample_reused=False,
            sample_application="",
            load_level="",
        )


if __name__ == "__main__":
    unittest.main()
