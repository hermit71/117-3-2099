"""Диалоги приложения, построенные на формах Qt Designer."""

from .about import AboutDialog
from .connection import ConnectionSettingsDialog
from .general import GeneralSettingsDialog
from .graph import GraphSettingsDialog
from .hand_regulator import HandRegulatorSettingsDialog

__all__ = [
    "AboutDialog",
    "ConnectionSettingsDialog",
    "GeneralSettingsDialog",
    "GraphSettingsDialog",
    "HandRegulatorSettingsDialog",
]

