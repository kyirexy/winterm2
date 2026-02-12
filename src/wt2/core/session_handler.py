"""Session management module."""

import uuid
from enum import Enum, auto
from typing import Dict, List, Optional, Any


class SessionStatus(Enum):
    """Session status enum."""

    INITIALIZED = auto()
    ACTIVE = auto()
    PAUSED = auto()
    CLOSED = auto()


class SessionState:
    """Represents the state of a terminal session."""

    def __init__(self, window_id: Optional[int] = None):
        """Initialize a session state.

        Args:
            window_id: The window ID associated with this session.
        """
        self.id: str = str(uuid.uuid4())
        self.window_id: Optional[int] = window_id
        self.status: SessionStatus = SessionStatus.INITIALIZED
        self.tabs: List[Dict[str, Any]] = []
        self.created_at = None
        self.start()

    def start(self, window_id: Optional[int] = None) -> None:
        """Start the session.

        Args:
            window_id: The window ID.
        """
        self.status = SessionStatus.ACTIVE
        if window_id:
            self.window_id = window_id

    def pause(self) -> None:
        """Pause the session."""
        self.status = SessionStatus.PAUSED

    def close(self) -> None:
        """Close the session."""
        self.status = SessionStatus.CLOSED

    def add_tab(self, tab_info: Dict[str, Any]) -> None:
        """Add a tab to the session.

        Args:
            tab_info: Tab information.
        """
        self.tabs.append(tab_info)

    def remove_tab(self, tab_id: int) -> bool:
        """Remove a tab from the session.

        Args:
            tab_id: The tab ID to remove.

        Returns:
            bool: True if tab was found and removed.
        """
        for i, tab in enumerate(self.tabs):
            if tab.get("id") == tab_id:
                self.tabs.pop(i)
                return True
        return False

    def get_tab(self, tab_id: int) -> Optional[Dict[str, Any]]:
        """Get a tab by ID.

        Args:
            tab_id: The tab ID.

        Returns:
            dict: Tab information or None.
        """
        for tab in self.tabs:
            if tab.get("id") == tab_id:
                return tab
        return None


class SessionManager:
    """Manages terminal sessions."""

    def __init__(self):
        """Initialize the session manager."""
        self._sessions: Dict[str, SessionState] = {}

    def create_session(self, window_id: Optional[int] = None) -> str:
        """Create a new session.

        Args:
            window_id: The window ID.

        Returns:
            str: Session ID.
        """
        session = SessionState(window_id)
        self._sessions[session.id] = session
        return session.id

    def get_session(self, session_id: str) -> Optional[SessionState]:
        """Get a session by ID.

        Args:
            session_id: The session ID.

        Returns:
            SessionState: The session or None.
        """
        return self._sessions.get(session_id)

    def update_session(
        self, session_id: str, data: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Update a session.

        Args:
            session_id: The session ID.
            data: Data to update.

        Returns:
            dict: Result of the operation.
        """
        session = self.get_session(session_id)
        if session is None:
            return {"success": False, "error": "Session not found"}

        for key, value in data.items():
            setattr(session, key, value)

        return {"success": True}

    def delete_session(self, session_id: str) -> Dict[str, Any]:
        """Delete a session.

        Args:
            session_id: The session ID.

        Returns:
            dict: Result of the operation.
        """
        if session_id not in self._sessions:
            return {"success": False, "error": "Session not found"}

        del self._sessions[session_id]
        return {"success": True}

    def list_sessions(self) -> List[str]:
        """List all session IDs.

        Returns:
            list: List of session IDs.
        """
        return list(self._sessions.keys())

    def clear_all(self) -> None:
        """Clear all sessions."""
        self._sessions.clear()
