"""Диалог настройки параметров соединения Modbus."""

from __future__ import annotations

import ipaddress
from typing import Dict, Optional

from PyQt6.QtGui import QIntValidator
from PyQt6.QtWidgets import QDialog, QMessageBox

from src.ui.designer_loader import load_ui
from src.utils.config import Config


class ConnectionSettingsDialog(QDialog):
    """Диалог ввода параметров подключения к ПЛК."""

    def __init__(self, parent=None, config: Optional[Config] = None) -> None:
        super().__init__(parent)
        self.config = config
        self._settings: Dict[str, float | int | str] = {}
        load_ui(self, "connection_settings_dialog.ui")
        self.ed_port.setValidator(QIntValidator(1, 65535, self))
        self._restore_from_config()

    def _restore_from_config(self) -> None:
        """Заполнить поля значениями из конфигурации."""

        if not self.config:
            return
        self.ed_host.setText(self.config.get("modbus", "host", "127.0.0.1"))
        self.ed_port.setText(str(self.config.get("modbus", "port", 502)))
        self.ed_timeout.setText(
            str(self.config.get("modbus", "timeout", 2.0))
        )
        self.ed_poll.setText(
            str(self.config.get("modbus", "poll_interval_ms", 100))
        )

    def _validate(self) -> bool:
        """Проверить корректность введённых данных."""

        host = self.ed_host.text().strip()
        port_text = self.ed_port.text().strip()
        timeout_text = self.ed_timeout.text().strip()
        poll_text = self.ed_poll.text().strip()

        try:
            ipaddress.ip_address(host)
        except ValueError:
            QMessageBox.warning(
                self,
                "Неверный IP",
                "Введите IP-адрес в формате 192.168.0.1",
            )
            return False

        if not port_text.isdigit():
            QMessageBox.warning(
                self,
                "Неверный порт",
                "Введите порт в диапазоне 1-65535, например, 502",
            )
            return False

        port = int(port_text)
        if not (1 <= port <= 65535):
            QMessageBox.warning(
                self,
                "Неверный порт",
                "Введите порт в диапазоне 1-65535, например, 502",
            )
            return False

        try:
            timeout = float(timeout_text)
            poll_interval = int(poll_text)
        except ValueError:
            QMessageBox.warning(
                self,
                "Неверные значения",
                "Таймаут и период опроса должны быть числами.",
            )
            return False

        if poll_interval <= 0:
            QMessageBox.warning(
                self,
                "Неверный период",
                "Период опроса должен быть положительным числом.",
            )
            return False

        self._settings = {
            "host": host,
            "port": port,
            "timeout": timeout,
            "poll_interval_ms": poll_interval,
        }
        return True

    def accept(self) -> None:  # noqa: D401
        """Сохранить введённые значения и закрыть диалог."""

        if not self._validate():
            return
        super().accept()

    @property
    def settings(self) -> Dict[str, float | int | str]:
        """Возвратить последние подтверждённые настройки."""

        return dict(self._settings)

    def apply_to_config(self, config: Config) -> None:
        """Применить подтверждённые параметры к конфигурации приложения."""

        if not self._settings:
            return
        config.cfg.setdefault("modbus", {})
        config.cfg.setdefault("ui", {})
        config.cfg["modbus"]["host"] = self._settings["host"]
        config.cfg["modbus"]["port"] = int(self._settings["port"])
        config.cfg["modbus"]["timeout"] = float(self._settings["timeout"])
        config.cfg["modbus"]["poll_interval_ms"] = int(
            self._settings["poll_interval_ms"]
        )

