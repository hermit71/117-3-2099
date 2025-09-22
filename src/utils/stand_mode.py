"""Глобальный индикатор режима работы стенда."""

from __future__ import annotations

from enum import Enum
from typing import Callable, List


class StandMode(Enum):
    """Перечисление режимов работы стенда."""

    PREPARATION = "preparation"
    TESTING = "testing"


class StandState:
    """Хранит текущее состояние стенда и уведомляет наблюдателей."""

    _mode: StandMode = StandMode.PREPARATION
    _observers: List[Callable[[StandMode], None]] = []

    @classmethod
    def mode(cls) -> StandMode:
        """Вернуть текущий режим стенда."""

        return cls._mode

    @classmethod
    def set_mode(cls, mode: StandMode) -> None:
        """Обновить режим стенда и уведомить подписчиков."""

        if cls._mode == mode:
            return
        cls._mode = mode
        for callback in list(cls._observers):
            callback(mode)

    @classmethod
    def subscribe(cls, callback: Callable[[StandMode], None]) -> None:
        """Добавить наблюдателя за изменением режима."""

        if callback not in cls._observers:
            cls._observers.append(callback)

    @classmethod
    def unsubscribe(cls, callback: Callable[[StandMode], None]) -> None:
        """Удалить наблюдателя."""

        if callback in cls._observers:
            cls._observers.remove(callback)
