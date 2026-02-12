"""Base terminal adapter class."""

from abc import ABC, abstractmethod
from typing import Dict, Any, Optional


class TerminalAdapter(ABC):
    """Abstract base class for terminal adapters."""

    name: str = "base"
    supports_colors: bool = True

    @abstractmethod
    def execute_command(self, command: str) -> Dict[str, Any]:
        """Execute a command in the terminal.

        Args:
            command: The command to execute.

        Returns:
            dict: Result of the operation.
        """
        raise NotImplementedError

    @abstractmethod
    def get_prompt(self) -> str:
        """Get the current terminal prompt.

        Returns:
            str: The prompt.
        """
        raise NotImplementedError

    @abstractmethod
    def change_directory(self, path: str) -> Dict[str, Any]:
        """Change the current directory.

        Args:
            path: The directory path.

        Returns:
            dict: Result of the operation.
        """
        raise NotImplementedError

    def is_available(self) -> bool:
        """Check if the terminal is available.

        Returns:
            bool: True if available.
        """
        return True
