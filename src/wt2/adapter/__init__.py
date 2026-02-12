"""Adapter package for platform-specific implementations."""

from .base import BaseAdapter, AdapterRegistry, AdapterInfo, ShellType
from .terminal import TerminalAdapter
from .powershell import PowerShellAdapter
from .cmd import CMDAdapter
from .wsl import WSLAdapter

__all__ = [
    "BaseAdapter",
    "AdapterRegistry",
    "AdapterInfo",
    "ShellType",
    "TerminalAdapter",
    "PowerShellAdapter",
    "CMDAdapter",
    "WSLAdapter",
]
