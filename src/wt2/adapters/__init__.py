"""Terminal adapter modules."""

from wt2.adapters.terminal_adapter import TerminalAdapter
from wt2.adapters.powershell_adapter import PowerShellAdapter
from wt2.adapters.wsl_adapter import WSLAdapter

__all__ = ["TerminalAdapter", "PowerShellAdapter", "WSLAdapter"]
