"""
Session management module.

Handles session lifecycle, connection pooling, and
state management for terminal sessions.
"""

from __future__ import annotations
import time
import uuid
from typing import Optional, Dict, List, Any, Callable
from dataclasses import dataclass, field
from enum import Enum
from concurrent.futures import ThreadPoolExecutor, Future

from .terminal import WindowsTerminalAPI


class SessionState(Enum):
    """Session state enumeration."""

    CREATED = "created"
    CONNECTING = "connecting"
    CONNECTED = "connected"
    DISCONNECTED = "disconnected"
    CLOSED = "closed"
    ERROR = "error"


@dataclass
class Session:
    """
    Represents a terminal session.

    Attributes:
        session_id: Unique identifier for the session.
        state: Current session state.
        shell_type: Type of shell (powershell, cmd, wsl).
        profile: Terminal profile name.
        cwd: Current working directory.
        created_at: Session creation timestamp.
        last_activity: Last activity timestamp.
        pane_id: Associated pane ID.
        tab_id: Associated tab ID.
    """

    session_id: str = field(default_factory=lambda: str(uuid.uuid4()))
    state: SessionState = SessionState.CREATED
    shell_type: str = "powershell"
    profile: str = "PowerShell"
    cwd: Optional[str] = None
    created_at: float = field(default_factory=time.time)
    last_activity: float = field(default_factory=time.time)
    pane_id: Optional[str] = None
    tab_id: Optional[int] = None

    def is_active(self) -> bool:
        """Check if the session is active."""
        return self.state in (SessionState.CREATED, SessionState.CONNECTED)

    def update_activity(self) -> None:
        """Update the last activity timestamp."""
        self.last_activity = time.time()


class SessionManager:
    """
    Manages terminal sessions with connection pooling.

    Provides a high-level interface for creating, managing,
    and destroying terminal sessions.
    """

    def __init__(
        self,
        max_connections: int = 10,
        session_timeout: float = 300.0,
        cleanup_interval: float = 60.0,
    ):
        """
        Initialize the session manager.

        Args:
            max_connections: Maximum number of concurrent connections.
            session_timeout: Session timeout in seconds (inactivity).
            cleanup_interval: Interval for cleanup tasks in seconds.
        """
        self.max_connections = max_connections
        self.session_timeout = session_timeout
        self.cleanup_interval = cleanup_interval

        self._sessions: Dict[str, Session] = {}
        self._api: WindowsTerminalAPI = WindowsTerminalAPI()
        self._executor: ThreadPoolExecutor = ThreadPoolExecutor(
            max_workers=max_connections
        )
        self._lock: Any = None  # Will be set below
        self._active_count: int = 0

        import threading
        self._lock = threading.RLock()

    def create_session(
        self,
        shell_type: str = "powershell",
        profile: Optional[str] = None,
        cwd: Optional[str] = None,
    ) -> Session:
        """
        Create a new terminal session.

        Args:
            shell_type: Type of shell (powershell, cmd, wsl).
            profile: Terminal profile name.
            cwd: Initial working directory.

        Returns:
            The created Session object.
        """
        with self._lock:
            # Check connection limit
            if self._active_count >= self.max_connections:
                raise RuntimeError(
                    f"Maximum connections ({self.max_connections}) reached"
                )

            session = Session(
                shell_type=shell_type,
                profile=profile or self._get_default_profile(shell_type),
                cwd=cwd,
            )

            # Connect the session
            try:
                self._api.connect()
                session.state = SessionState.CONNECTED
            except Exception:
                session.state = SessionState.ERROR

            self._sessions[session.session_id] = session
            self._active_count += 1

            return session

    def get_session(self, session_id: str) -> Optional[Session]:
        """
        Retrieve a session by ID.

        Args:
            session_id: The session ID to find.

        Returns:
            Session object if found, None otherwise.
        """
        return self._sessions.get(session_id)

    def list_sessions(
        self,
        state: Optional[SessionState] = None,
        shell_type: Optional[str] = None,
    ) -> List[Session]:
        """
        List sessions with optional filtering.

        Args:
            state: Filter by session state.
            shell_type: Filter by shell type.

        Returns:
            List of matching sessions.
        """
        sessions = list(self._sessions.values())

        if state:
            sessions = [s for s in sessions if s.state == state]

        if shell_type:
            sessions = [s for s in sessions if s.shell_type == shell_type]

        return sessions

    def close_session(self, session_id: str) -> bool:
        """
        Close a session.

        Args:
            session_id: The session ID to close.

        Returns:
            True if session was closed, False if not found.
        """
        with self._lock:
            session = self._sessions.get(session_id)
            if not session:
                return False

            session.state = SessionState.CLOSED
            self._sessions.pop(session_id)
            self._active_count = max(0, self._active_count - 1)

            # Close associated resources
            if session.tab_id:
                try:
                    self._api.close_tab(session.tab_id)
                except Exception:
                    pass

            return True

    def send_command(
        self,
        session_id: str,
        command: str,
        timeout: float = 10.0,
    ) -> dict[str, Any]:
        """
        Send a command to a session.

        Args:
            session_id: Target session ID.
            command: Command to send.
            timeout: Command execution timeout.

        Returns:
            Response dictionary.

        Raises:
            ValueError: If session not found.
        """
        session = self.get_session(session_id)
        if not session:
            raise ValueError(f"Session not found: {session_id}")

        session.update_activity()

        # Execute the command via the API
        response = self._api.execute_command(
            command=command,
            pane_id=session.pane_id,
            timeout=timeout,
        )

        return response

    def send_text(
        self,
        session_id: str,
        text: str,
    ) -> dict[str, Any]:
        """
        Send raw text to a session.

        Args:
            session_id: Target session ID.
            text: Text to send.

        Returns:
            Response dictionary.
        """
        session = self.get_session(session_id)
        if not session:
            raise ValueError(f"Session not found: {session_id}")

        session.update_activity()

        return self._api.send_text(
            text=text,
            pane_id=session.pane_id,
        )

    def focus_session(self, session_id: str) -> dict[str, Any]:
        """
        Focus a session's pane.

        Args:
            session_id: Target session ID.

        Returns:
            Response dictionary.
        """
        session = self.get_session(session_id)
        if not session:
            raise ValueError(f"Session not found: {session_id}")

        if session.pane_id:
            return self._api.focus_pane(session.pane_id)
        elif session.tab_id:
            return self._api.focus_tab(session.tab_id)

        return {"success": False, "reason": "No pane or tab associated"}

    def cleanup_inactive(self) -> int:
        """
        Clean up inactive sessions.

        Returns:
            Number of sessions cleaned up.
        """
        current_time = time.time()
        to_remove = []

        for session_id, session in self._sessions.items():
            if (
                session.state in (SessionState.DISCONNECTED, SessionState.ERROR)
                or (current_time - session.last_activity) > self.session_timeout
            ):
                to_remove.append(session_id)

        for session_id in to_remove:
            self.close_session(session_id)

        return len(to_remove)

    def get_stats(self) -> dict[str, Any]:
        """
        Get session manager statistics.

        Returns:
            Statistics dictionary.
        """
        with self._lock:
            stats = {
                "total_sessions": len(self._sessions),
                "active_connections": self._active_count,
                "max_connections": self.max_connections,
                "sessions_by_state": {},
                "sessions_by_shell": {},
            }

            for session in self._sessions.values():
                # Count by state
                state_name = session.state.value
                stats["sessions_by_state"][state_name] = (
                    stats["sessions_by_state"].get(state_name, 0) + 1
                )

                # Count by shell type
                shell = session.shell_type
                stats["sessions_by_shell"][shell] = (
                    stats["sessions_by_shell"].get(shell, 0) + 1
                )

            return stats

    def _get_default_profile(self, shell_type: str) -> str:
        """
        Get the default profile name for a shell type.

        Args:
            shell_type: The shell type.

        Returns:
            Profile name.
        """
        profile_map = {
            "powershell": "PowerShell",
            "cmd": "Command Prompt",
            "wsl": "WSL",
        }
        return profile_map.get(shell_type, "PowerShell")

    def shutdown(self) -> None:
        """Shutdown the session manager and close all sessions."""
        with self._lock:
            # Close all sessions
            for session_id in list(self._sessions.keys()):
                self.close_session(session_id)

            # Shutdown executor
            self._executor.shutdown(wait=True)

            # Disconnect API
            self._api.disconnect()
