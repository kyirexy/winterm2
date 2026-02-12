"""
winterm2 - Windows Terminal CLI automation tool (it2 for Windows).

A native Windows CLI tool for automating Windows Terminal,
PowerShell 7+, CMD, and WSL2 shells.
"""

__version__ = "0.1.0"
__author__ = "winterm2 team"

from .cli import cli

__all__ = ["cli", "__version__"]
