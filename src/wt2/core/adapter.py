"""
Base adapter class for terminal/shell interactions.

Defines the interface that all platform-specific adapters
must implement.
"""

from __future__ import annotations
import abc
from typing import Optional, Dict, Any, List, Type, TypeVar, ClassVar
from dataclasses import dataclass
from enum import Enum


class ShellType(Enum):
    """Supported shell types."""

    WINDOWS_TERMINAL = "terminal"
    POWERSHELL = "powershell"
    POWERSHELL_CORE = "pwsh"
    CMD = "cmd"
    WSL = "wsl"
    UNKNOWN = "unknown"


@dataclass
class AdapterInfo:
    """Information about an adapter."""

    name: str
    shell_type: ShellType
    version: str
    is_available: bool
    executable_path: Optional[str] = None
    default_args: List[str] = None

    def __post_init__(self):
        if self.default_args is None:
            self.default_args = []


T = TypeVar("T", bound="BaseAdapter")


class BaseAdapter(abc.ABC):
    """
    Abstract base class for terminal/shell adapters.

    All platform-specific adapters must inherit from this class
    and implement all abstract methods.
    """

    # Class-level registration
    _registry: ClassVar[Dict[ShellType, Type["BaseAdapter"]]] = {}
    _default_adapter: ClassVar[Optional[ShellType]] = None

    @classmethod
    def register(cls, shell_type: ShellType) -> callable:
        """
        Decorator to register an adapter for a shell type.

        Args:
            shell_type: The shell type to register for.

        Returns:
            Decorator function.
        """
        def decorator(adapter_cls: Type[T]) -> Type[T]:
            cls._registry[shell_type] = adapter_cls
            return adapter_cls
        return decorator

    @classmethod
    def get_adapter(cls, shell_type: ShellType) -> Optional[Type["BaseAdapter"]]:
        """
        Get the adapter class for a shell type.

        Args:
            shell_type: The shell type.

        Returns:
            Adapter class or None if not found.
        """
        return cls._registry.get(shell_type)

    @classmethod
    def create(cls, shell_type: ShellType, **kwargs) -> "BaseAdapter":
        """
        Create an adapter instance for a shell type.

        Args:
            shell_type: The shell type.
            **kwargs: Additional arguments for the adapter.

        Returns:
            Adapter instance.

        Raises:
            ValueError: If no adapter is registered for the shell type.
        """
        adapter_cls = cls.get_adapter(shell_type)
        if not adapter_cls:
            raise ValueError(f"No adapter registered for shell type: {shell_type}")
        return adapter_cls(**kwargs)

    @classmethod
    def get_available_adapters(cls) -> List[ShellType]:
        """Get list of available (registered) adapters."""
        return list(cls._registry.keys())

    @property
    @abc.abstractmethod
    def info(self) -> AdapterInfo:
        """Get adapter information."""
        pass

    @abc.abstractmethod
    def is_available(self) -> bool:
        """Check if the shell is available."""
        pass

    @abc.abstractmethod
    def execute(
        self,
        command: str,
        cwd: Optional[str] = None,
        env: Optional[Dict[str, str]] = None,
        timeout: Optional[float] = None,
    ) -> Dict[str, Any]:
        """
        Execute a command in the shell.

        Args:
            command: Command to execute.
            cwd: Working directory.
            env: Environment variables.
            timeout: Execution timeout.

        Returns:
            Response with stdout, stderr, and exit code.
        """
        pass

    @abc.abstractmethod
    def start_session(
        self,
        cwd: Optional[str] = None,
        env: Optional[Dict[str, str]] = None,
    ) -> str:
        """
        Start an interactive session.

        Args:
            cwd: Working directory.
            env: Environment variables.

        Returns:
            Session identifier.
        """
        pass

    @abc.abstractmethod
    def end_session(self, session_id: str) -> bool:
        """
        End an interactive session.

        Args:
            session_id: Session identifier.

        Returns:
            True if successful.
        """
        pass

    @abc.abstractmethod
    def send_input(
        self,
        session_id: str,
        text: str,
        wait_for_prompt: bool = False,
    ) -> bool:
        """
        Send input to a session.

        Args:
            session_id: Session identifier.
            text: Text to send.
            wait_for_prompt: Wait for prompt after sending.

        Returns:
            True if successful.
        """
        pass

    @abc.abstractmethod
    def get_prompt(self, session_id: str) -> str:
        """
        Get the current shell prompt.

        Args:
            session_id: Session identifier.

        Returns:
            Current prompt string.
        """
        pass

    @abc.abstractmethod
    def resize_terminal(
        self,
        session_id: str,
        rows: int,
        cols: int,
    ) -> bool:
        """
        Resize the terminal.

        Args:
            session_id: Session identifier.
            rows: Number of rows.
            cols: Number of columns.

        Returns:
            True if successful.
        """
        pass

    @abc.abstractmethod
    def get_environment(
        self,
        session_id: str,
        *variables: str,
    ) -> Dict[str, str]:
        """
        Get environment variables from a session.

        Args:
            session_id: Session identifier.
            *variables: Variable names to retrieve.

        Returns:
            Dictionary of variable names to values.
        """
        pass

    @abc.abstractmethod
    def set_environment(
        self,
        session_id: str,
        **variables: str,
    ) -> bool:
        """
        Set environment variables in a session.

        Args:
            session_id: Session identifier.
            **variables: Variables to set.

        Returns:
            True if successful.
        """
        pass

    @abc.abstractmethod
    def get_working_directory(self, session_id: str) -> str:
        """
        Get the current working directory.

        Args:
            session_id: Session identifier.

        Returns:
            Current working directory.
        """
        pass

    @abc.abstractmethod
    def change_directory(self, session_id: str, path: str) -> bool:
        """
        Change the working directory.

        Args:
            session_id: Session identifier.
            path: New directory path.

        Returns:
            True if successful.
        """
        pass

    @abc.abstractmethod
    def clear_screen(self, session_id: str) -> bool:
        """
        Clear the terminal screen.

        Args:
            session_id: Session identifier.

        Returns:
            True if successful.
        """
        pass

    @abc.abstractmethod
    def get_exit_code(self, session_id: str) -> Optional[int]:
        """
        Get the last exit code from the session.

        Args:
            session_id: Session identifier.

        Returns:
            Exit code or None.
        """
        pass

    @abc.abstractmethod
    def kill_session(self, session_id: str, signal: int = 9) -> bool:
        """
        Kill a session.

        Args:
            session_id: Session identifier.
            signal: Signal to send.

        Returns:
            True if successful.
        """
        pass


class AdapterRegistry:
    """
    Registry for managing shell adapters.

    Provides a centralized way to discover and manage
    available shell adapters.
    """

    def __init__(self):
        """Initialize the adapter registry."""
        self._adapters: Dict[ShellType, BaseAdapter] = {}
        self._auto_detect_order: List[ShellType] = [
            ShellType.POWERSHELL_CORE,
            ShellType.POWERSHELL,
            ShellType.CMD,
            ShellType.WSL,
        ]

    def register(self, adapter: BaseAdapter) -> None:
        """
        Register an adapter instance.

        Args:
            adapter: The adapter to register.
        """
        self._adapters[adapter.info.shell_type] = adapter

    def unregister(self, shell_type: ShellType) -> None:
        """
        Unregister an adapter.

        Args:
            shell_type: The shell type to unregister.
        """
        self._adapters.pop(shell_type, None)

    def get(self, shell_type: ShellType) -> Optional[BaseAdapter]:
        """
        Get an adapter by shell type.

        Args:
            shell_type: The shell type.

        Returns:
            Adapter or None if not found.
        """
        return self._adapters.get(shell_type)

    def get_all(self) -> List[BaseAdapter]:
        """Get all registered adapters."""
        return list(self._adapters.values())

    def get_available(self) -> List[BaseAdapter]:
        """Get all available (installed and usable) adapters."""
        return [a for a in self.get_all() if a.is_available()]

    def get_auto_detect_order(self) -> List[ShellType]:
        """Get the order for auto-detection."""
        return self._auto_detect_order.copy()

    def set_auto_detect_order(self, order: List[ShellType]) -> None:
        """
        Set the order for auto-detection.

        Args:
            order: List of shell types in detection order.
        """
        self._auto_detect_order = order

    def auto_detect(self) -> Optional[BaseAdapter]:
        """
        Auto-detect the best available shell.

        Returns:
            First available adapter or None.
        """
        for shell_type in self._auto_detect_order:
            adapter = self.get(shell_type)
            if adapter and adapter.is_available():
                return adapter
        return None

    def detect_and_create(self) -> Optional[BaseAdapter]:
        """
        Auto-detect and create an adapter.

        Returns:
            Created adapter or None.
        """
        adapter = self.auto_detect()
        if adapter:
            return adapter

        # Try creating adapters for each type
        for shell_type in self._auto_detect_order:
            try:
                adapter = BaseAdapter.create(shell_type)
                if adapter.is_available():
                    self.register(adapter)
                    return adapter
            except (ValueError, Exception):
                continue

        return None
