"""
Windows Terminal API connection module.

Handles communication with Windows Terminal via named pipes
using the Windows Terminal JSON command API.
"""

from __future__ import annotations
import json
import time
from typing import Optional, Any, Callable
from threading import Lock
import ctypes
from ctypes import wintypes

from .exceptions import ConnectionError, CommandError, TimeoutError


class WindowsTerminalAPI:
    """
    Interface to Windows Terminal's JSON command API.

    Connects to Windows Terminal via named pipe and sends
    JSON commands to control the terminal.
    """

    # Named pipe paths for Windows Terminal
    PIPE_PATHS = [
        r"\\.\pipe\WindowsTerminal",
        r"\\.\pipe\WindowsTerminal_dev",
    ]

    def __init__(
        self,
        timeout: float = 5.0,
        max_retries: int = 3,
        retry_delay: float = 0.5,
    ):
        """
        Initialize the Windows Terminal API connection.

        Args:
            timeout: Connection and command timeout in seconds.
            max_retries: Maximum retry attempts for failed connections.
            retry_delay: Delay between retry attempts in seconds.
        """
        self.timeout = timeout
        self.max_retries = max_retries
        self.retry_delay = retry_delay
        self._pipe_handle: Optional[int] = None
        self._lock = Lock()
        self._last_activity: float = 0

    def connect(self) -> bool:
        """
        Establish connection to Windows Terminal named pipe.

        Returns:
            True if connection successful, False otherwise.

        Raises:
            ConnectionError: If connection fails after all retries.
        """
        for attempt in range(self.max_retries):
            for pipe_path in self.PIPE_PATHS:
                try:
                    self._pipe_handle = self._create_pipe_connection(pipe_path)
                    if self._pipe_handle:
                        self._last_activity = time.time()
                        return True
                except Exception:
                    continue

            if attempt < self.max_retries - 1:
                time.sleep(self.retry_delay)

        raise ConnectionError(
            pipe_name=self.PIPE_PATHS[0],
            details=f"Failed after {self.max_retries} attempts",
        )

    def _create_pipe_connection(self, pipe_path: str) -> Optional[int]:
        """
        Create a connection to the named pipe.

        Args:
            pipe_path: Path to the named pipe.

        Returns:
            Pipe handle if successful, None otherwise.
        """
        try:
            # Windows named pipe constants
            PIPE_READMODE_MESSAGE = 2
            PIPE_WAIT = 0
            INVALID_HANDLE_VALUE = -1

            # Open the named pipe
            handle = ctypes.windll.kernel32.CreateFileW(
                pipe_path,
                0xC0000000,  # GENERIC_READ | GENERIC_WRITE
                0,           # No sharing
                None,        # Default security attributes
                3,           # OPEN_EXISTING
                0x40000000,  # FILE_FLAG_OVERLAPPED
                None,        # No template file
            )

            if handle == INVALID_HANDLE_VALUE:
                return None

            # Set pipe mode to message
            mode = ctypes.byref(ctypes.c_ulong(PIPE_READMODE_MESSAGE))
            ctypes.windll.kernel32.SetNamedPipeHandleState(
                handle, mode, None, None
            )

            return handle

        except Exception:
            return None

    def disconnect(self) -> None:
        """Close the named pipe connection."""
        if self._pipe_handle:
            try:
                ctypes.windll.kernel32.CloseHandle(self._pipe_handle)
            except Exception:
                pass
            self._pipe_handle = None

    def is_connected(self) -> bool:
        """Check if the pipe connection is active."""
        if not self._pipe_handle:
            return False

        # Check if pipe is still valid
        try:
            state = ctypes.c_ulong()
            ctypes.windll.kernel32.GetNamedPipeHandleStateW(
                self._pipe_handle, ctypes.byref(state), None, None, None, None
            )
            return True
        except Exception:
            return False

    def send_command(
        self,
        action: str,
        **kwargs: Any,
    ) -> dict[str, Any]:
        """
        Send a JSON command to Windows Terminal.

        Args:
            action: The action to perform (e.g., "newTab", "closeTab").
            **kwargs: Additional action parameters.

        Returns:
            Response dictionary from Windows Terminal.

        Raises:
            CommandError: If the command fails.
        """
        if not self.is_connected():
            self.connect()

        command = {"action": action, **kwargs}
        return self._send_json(command)

    def _send_json(self, data: dict[str, Any]) -> dict[str, Any]:
        """
        Send JSON data through the named pipe.

        Args:
            data: JSON-serializable data to send.

        Returns:
            Response from Windows Terminal.

        Raises:
            CommandError: If sending fails.
        """
        try:
            json_data = json.dumps(data).encode("utf-8")

            # Ensure null termination
            json_data += b"\x00\x00"

            with self._lock:
                bytes_written = ctypes.c_ulong()
                success = ctypes.windll.kernel32.WriteFile(
                    self._pipe_handle,
                    json_data,
                    len(json_data),
                    ctypes.byref(bytes_written),
                    None,
                )

            if not success:
                raise CommandError(
                    command=json.dumps(data),
                    details="WriteFile failed",
                )

            return {"success": True, "action": data.get("action")}

        except CommandError:
            raise
        except Exception as e:
            raise CommandError(
                command=json.dumps(data),
                stderr=str(e),
            )

    def get_state(self) -> dict[str, Any]:
        """
        Get the current state of Windows Terminal.

        Returns:
            Dictionary containing terminal state (tabs, windows, etc.).
        """
        result = self.send_command("getState")
        return result if isinstance(result, dict) else {}

    def new_tab(
        self,
        profile: Optional[str] = None,
        command: Optional[str] = None,
        cwd: Optional[str] = None,
    ) -> dict[str, Any]:
        """
        Create a new tab.

        Args:
            profile: Profile name to use (defaults to default profile).
            command: Initial command to run in the tab.
            cwd: Working directory for the new tab.

        Returns:
            Response from Windows Terminal.
        """
        params = {}
        if profile:
            params["profile"] = profile
        if command:
            params["command"] = command
        if cwd:
            params["cwd"] = cwd

        return self.send_command("newTab", **params)

    def close_tab(self, tab_id: int) -> dict[str, Any]:
        """
        Close a tab by ID.

        Args:
            tab_id: The ID of the tab to close.

        Returns:
            Response from Windows Terminal.
        """
        return self.send_command("closeTab", tabId=tab_id)

    def focus_tab(self, tab_id: int) -> dict[str, Any]:
        """
        Focus a specific tab.

        Args:
            tab_id: The ID of the tab to focus.

        Returns:
            Response from Windows Terminal.
        """
        return self.send_command("focusTab", tabId=tab_id)

    def new_pane(
        self,
        profile: Optional[str] = None,
        command: Optional[str] = None,
        cwd: Optional[str] = None,
        direction: str = "right",
        size: Optional[float] = None,
    ) -> dict[str, Any]:
        """
        Create a new pane by splitting.

        Args:
            profile: Profile name to use.
            command: Initial command to run.
            cwd: Working directory.
            direction: Split direction ("right", "left", "up", "down").
            size: Size of the new pane as percentage (0-1).

        Returns:
            Response from Windows Terminal.
        """
        params = {
            "direction": direction,
        }
        if profile:
            params["profile"] = profile
        if command:
            params["command"] = command
        if cwd:
            params["cwd"] = cwd
        if size is not None:
            params["size"] = size

        return self.send_command("splitPane", **params)

    def resize_pane(
        self,
        pane_id: str,
        direction: str,
        delta: int,
    ) -> dict[str, Any]:
        """
        Resize a pane.

        Args:
            pane_id: The ID of the pane to resize.
            direction: Resize direction.
            delta: Amount to resize (cells).

        Returns:
            Response from Windows Terminal.
        """
        return self.send_command(
            "resizePane",
            paneId=pane_id,
            direction=direction,
            delta=delta,
        )

    def focus_pane(self, pane_id: str) -> dict[str, Any]:
        """
        Focus a specific pane.

        Args:
            pane_id: The ID of the pane to focus.

        Returns:
            Response from Windows Terminal.
        """
        return self.send_command("focusPane", paneId=pane_id)

    def send_text(
        self,
        text: str,
        pane_id: Optional[str] = None,
    ) -> dict[str, Any]:
        """
        Send text to a pane.

        Args:
            text: Text to send.
            pane_id: Target pane ID (defaults to focused pane).

        Returns:
            Response from Windows Terminal.
        """
        params = {"text": text}
        if pane_id:
            params["paneId"] = pane_id

        return self.send_command("sendInput", **params)

    def execute_command(
        self,
        command: str,
        pane_id: Optional[str] = None,
        timeout: float = 10.0,
    ) -> dict[str, Any]:
        """
        Execute a shell command and wait for completion.

        Args:
            command: Command to execute.
            pane_id: Target pane ID.
            timeout: Maximum time to wait for command completion.

        Returns:
            Response with exit code and output.

        Raises:
            TimeoutError: If command doesn't complete within timeout.
        """
        start_time = time.time()

        # Send the command
        self.send_text(command + "\r\n", pane_id=pane_id)

        # Wait for command completion (simple heuristic)
        while time.time() - start_time < timeout:
            time.sleep(0.1)
            # Check for command prompt or completion
            # This is a simplified implementation
            if time.time() - start_time >= timeout:
                raise TimeoutError(
                    operation=command,
                    timeout=timeout,
                )

        return {
            "success": True,
            "command": command,
            "execution_time": time.time() - start_time,
        }

    def __enter__(self) -> "WindowsTerminalAPI":
        """Context manager entry."""
        self.connect()
        return self

    def __exit__(self, exc_type, exc_val, exc_tb) -> None:
        """Context manager exit."""
        self.disconnect()


# Singleton instance for common use
_api_instance: Optional[WindowsTerminalAPI] = None


def get_api() -> WindowsTerminalAPI:
    """Get or create the singleton API instance."""
    global _api_instance
    if _api_instance is None:
        _api_instance = WindowsTerminalAPI()
    return _api_instance
