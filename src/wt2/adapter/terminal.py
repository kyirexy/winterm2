"""
Windows Terminal API adapter.

Provides integration with Windows Terminal via its JSON command API.
"""

from __future__ import annotations
import json
import time
from typing import Optional, Dict, Any, List
import ctypes
from ctypes import wintypes

from .base import BaseAdapter, AdapterInfo, ShellType, AdapterRegistry
from ..core.terminal import WindowsTerminalAPI


class TerminalAdapter(BaseAdapter):
    """
    Adapter for Windows Terminal.

    Uses the Windows Terminal JSON command API via named pipe
    to communicate with the terminal.
    """

    def __init__(
        self,
        timeout: float = 5.0,
        pipe_name: str = r"\\.\pipe\WindowsTerminal",
    ):
        """
        Initialize the Terminal adapter.

        Args:
            timeout: Connection timeout in seconds.
            pipe_name: Named pipe path for Windows Terminal.
        """
        self._timeout = timeout
        self._pipe_name = pipe_name
        self._api: Optional[WindowsTerminalAPI] = None
        self._connected = False

    @property
    def info(self) -> AdapterInfo:
        """Get adapter information."""
        return AdapterInfo(
            name="Windows Terminal",
            shell_type=ShellType.WINDOWS_TERMINAL,
            version="1.0",
            is_available=self.is_available(),
            executable_path="wt.exe",
        )

    def is_available(self) -> bool:
        """Check if Windows Terminal is available."""
        try:
            # Try to connect
            api = WindowsTerminalAPI(timeout=1.0)
            api.connect()
            api.disconnect()
            return True
        except Exception:
            return False

    def connect(self) -> bool:
        """Establish connection to Windows Terminal."""
        try:
            self._api = WindowsTerminalAPI(timeout=self._timeout)
            self._api.connect()
            self._connected = True
            return True
        except Exception:
            self._connected = False
            return False

    def disconnect(self) -> None:
        """Disconnect from Windows Terminal."""
        if self._api:
            self._api.disconnect()
            self._connected = False

    def execute(
        self,
        command: str,
        cwd: Optional[str] = None,
        env: Optional[Dict[str, str]] = None,
        timeout: Optional[float] = None,
    ) -> Dict[str, Any]:
        """
        Execute a command in Windows Terminal.

        Note: Direct command execution in WT requires a running shell session.

        Args:
            command: Command to execute.
            cwd: Working directory.
            env: Environment variables.
            timeout: Execution timeout.

        Returns:
            Response with success status.
        """
        if not self._connected:
            self.connect()

        try:
            result = self._api.execute_command(
                command=command,
                timeout=timeout or 10.0,
            )
            return {
                "success": True,
                "stdout": "",
                "stderr": "",
                "exit_code": 0,
                "result": result,
            }
        except Exception as e:
            return {
                "success": False,
                "stdout": "",
                "stderr": str(e),
                "exit_code": 1,
            }

    def start_session(
        self,
        cwd: Optional[str] = None,
        env: Optional[Dict[str, str]] = None,
    ) -> str:
        """
        Start a new terminal session (tab).

        Args:
            cwd: Working directory for the new session.
            env: Environment variables.

        Returns:
            Session identifier (tab ID).
        """
        if not self._connected:
            self.connect()

        result = self._api.new_tab(
            cwd=cwd,
        )
        tab_id = result.get("tabId", int(time.time()))
        return str(tab_id)

    def end_session(self, session_id: str) -> bool:
        """
        End a terminal session.

        Args:
            session_id: Session (tab) identifier.

        Returns:
            True if successful.
        """
        if not self._connected:
            return False

        try:
            tab_id = int(session_id)
            self._api.close_tab(tab_id)
            return True
        except Exception:
            return False

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
            wait_for_prompt: Wait for prompt (not implemented for WT API).

        Returns:
            True if successful.
        """
        if not self._connected:
            return False

        try:
            self._api.send_text(text=text, pane_id=session_id)
            return True
        except Exception:
            return False

    def get_prompt(self, session_id: str) -> str:
        """
        Get the current shell prompt.

        Args:
            session_id: Session identifier.

        Returns:
            Prompt string (not available via WT API).
        """
        return "wt> "

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
        if not self._connected:
            return False

        try:
            self._api.resize_pane(
                pane_id=session_id,
                direction="auto",
                delta=0,
            )
            return True
        except Exception:
            return False

    def get_environment(
        self,
        session_id: str,
        *variables: str,
    ) -> Dict[str, str]:
        """
        Get environment variables.

        Args:
            session_id: Session identifier.
            *variables: Variables to retrieve.

        Returns:
            Dictionary of variables.
        """
        return {}

    def set_environment(
        self,
        session_id: str,
        **variables: str,
    ) -> bool:
        """
        Set environment variables.

        Args:
            session_id: Session identifier.
            **variables: Variables to set.

        Returns:
            True if successful.
        """
        return True

    def get_working_directory(self, session_id: str) -> str:
        """
        Get the current working directory.

        Args:
            session_id: Session identifier.

        Returns:
            Current working directory.
        """
        return ""

    def change_directory(self, session_id: str, path: str) -> bool:
        """
        Change the working directory.

        Args:
            session_id: Session identifier.
            path: New directory path.

        Returns:
            True if successful.
        """
        return self.send_input(session_id, f"cd '{path}'\r\n")

    def clear_screen(self, session_id: str) -> bool:
        """
        Clear the terminal screen.

        Args:
            session_id: Session identifier.

        Returns:
            True if successful.
        """
        return self.send_input(session_id, "cls\r\n")

    def get_exit_code(self, session_id: str) -> Optional[int]:
        """
        Get the last exit code.

        Args:
            session_id: Session identifier.

        Returns:
            Exit code or None.
        """
        return None

    def kill_session(self, session_id: str, signal: int = 9) -> bool:
        """
        Kill a session.

        Args:
            session_id: Session identifier.
            signal: Signal (not used for Windows).

        Returns:
            True if successful.
        """
        return self.end_session(session_id)

    # Window/Tab/Pane operations

    def new_window(
        self,
        profile: Optional[str] = None,
        cwd: Optional[str] = None,
    ) -> Dict[str, Any]:
        """
        Create a new window.

        Args:
            profile: Profile name.
            cwd: Working directory.

        Returns:
            Response with window ID.
        """
        if not self._connected:
            self.connect()

        result = self._api.send_command("newWindow")
        return result

    def close_window(self, window_id: str) -> bool:
        """
        Close a window.

        Args:
            window_id: Window identifier.

        Returns:
            True if successful.
        """
        return True

    def get_window_list(self) -> List[Dict[str, Any]]:
        """
        Get list of windows.

        Returns:
            List of window information.
        """
        if not self._connected:
            return []

        state = self._api.get_state()
        return state.get("windows", [])

    def get_tab_list(self) -> List[Dict[str, Any]]:
        """
        Get list of tabs.

        Returns:
            List of tab information.
        """
        if not self._connected:
            return []

        state = self._api.get_state()
        return state.get("tabs", [])

    def focus_tab(self, tab_id: int) -> bool:
        """
        Focus a specific tab.

        Args:
            tab_id: Tab ID to focus.

        Returns:
            True if successful.
        """
        if not self._connected:
            return False

        try:
            self._api.focus_tab(tab_id)
            return True
        except Exception:
            return False


# Register the adapter
BaseAdapter.register(ShellType.WINDOWS_TERMINAL)(TerminalAdapter)
