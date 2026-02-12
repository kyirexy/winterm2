"""
Custom exceptions for winterm2 with error codes.

Error Code Reference:
    WT001-WT009: Connection errors
    WT010-WT019: Command execution errors
    WT020-WT029: Shell detection errors
    WT030-WT039: Path conversion errors
    WT040-WT049: Configuration errors
    WT050-WT059: Window/Tab/Pane errors
"""

from __future__ import annotations
from typing import Optional


class WintermError(Exception):
    """Base exception for winterm2."""

    error_code: str = "WT000"
    message: str = "Unknown error occurred"

    def __init__(
        self,
        message: Optional[str] = None,
        details: Optional[str] = None,
        suggestion: Optional[str] = None,
    ):
        self.message = message or self.message
        self.details = details
        self.suggestion = suggestion
        super().__init__(self._format_message())

    def _format_message(self) -> str:
        """Format the error message with code and details."""
        parts = [f"[{self.error_code}] {self.message}"]
        if self.details:
            parts.append(f"Details: {self.details}")
        if self.suggestion:
            parts.append(f"Suggestion: {self.suggestion}")
        return " | ".join(parts)

    def __str__(self) -> str:
        return self._format_message()


class ConnectionError(WintermError):
    """Failed to connect to Windows Terminal."""

    error_code = "WT001"

    def __init__(self, pipe_name: str, details: Optional[str] = None):
        self.pipe_name = pipe_name
        super().__init__(
            message=f"Failed to connect to Windows Terminal via {pipe_name}",
            details=details,
            suggestion="Ensure Windows Terminal is running and the pipe exists.",
        )


class CommandError(WintermError):
    """Failed to execute a command in the terminal."""

    error_code = "WT010"

    def __init__(
        self,
        command: str,
        exit_code: Optional[int] = None,
        stderr: Optional[str] = None,
    ):
        self.command = command
        self.exit_code = exit_code
        self.stderr = stderr
        super().__init__(
            message=f"Command execution failed: {command}",
            details=f"Exit code: {exit_code}" if exit_code else None,
            suggestion="Check the command syntax and ensure the shell is available.",
        )


class ShellNotFoundError(WintermError):
    """Specified shell was not found."""

    error_code = "WT020"

    def __init__(
        self,
        shell_name: str,
        search_paths: Optional[list[str]] = None,
    ):
        self.shell_name = shell_name
        self.search_paths = search_paths
        super().__init__(
            message=f"Shell not found: {shell_name}",
            details=f"Searched in: {search_paths}" if search_paths else None,
            suggestion=f"Ensure {shell_name} is installed and in your PATH.",
        )


class InvalidArgumentError(WintermError):
    """Invalid argument provided to a command."""

    error_code = "WT030"

    def __init__(
        self,
        argument: str,
        reason: str,
        valid_values: Optional[list[str]] = None,
    ):
        self.argument = argument
        self.reason = reason
        self.valid_values = valid_values
        super().__init__(
            message=f"Invalid argument '{argument}': {reason}",
            details=f"Valid values: {valid_values}" if valid_values else None,
        )


class WindowNotFoundError(WintermError):
    """Window was not found."""

    error_code = "WT050"

    def __init__(self, window_id: str):
        self.window_id = window_id
        super().__init__(
            message=f"Window not found: {window_id}",
            suggestion="Use 'wt2 window list' to see available windows.",
        )


class TabNotFoundError(WintermError):
    """Tab was not found."""

    error_code = "WT051"

    def __init__(self, tab_id: str):
        self.tab_id = tab_id
        super().__init__(
            message=f"Tab not found: {tab_id}",
            suggestion="Use 'wt2 tab list' to see available tabs.",
        )


class PaneNotFoundError(WintermError):
    """Pane was not found."""

    error_code = "WT052"

    def __init__(self, pane_id: str):
        self.pane_id = pane_id
        super().__init__(
            message=f"Pane not found: {pane_id}",
            suggestion="Use 'wt2 pane list' to see available panes.",
        )


class ConfigError(WintermError):
    """Configuration file error."""

    error_code = "WT040"

    def __init__(
        self,
        config_path: str,
        reason: str,
    ):
        self.config_path = config_path
        self.reason = reason
        super().__init__(
            message=f"Configuration error in {config_path}: {reason}",
        )


class TimeoutError(WintermError):
    """Operation timed out."""

    error_code = "WT060"

    def __init__(self, operation: str, timeout: float):
        self.operation = operation
        self.timeout = timeout
        super().__init__(
            message=f"Operation timed out: {operation}",
            details=f"Timeout: {timeout}s",
            suggestion="Try increasing the timeout or reducing the operation scope.",
        )
