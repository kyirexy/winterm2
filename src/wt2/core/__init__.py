"""Core business logic package."""

from .session import SessionManager
from .terminal import WindowsTerminalAPI
from .exceptions import (
    WintermError,
    ConnectionError as WintermConnectionError,
    CommandError,
    ShellNotFoundError,
    InvalidArgumentError,
)

__all__ = [
    "SessionManager",
    "WindowsTerminalAPI",
    "WintermError",
    "WintermConnectionError",
    "CommandError",
    "ShellNotFoundError",
    "InvalidArgumentError",
]
