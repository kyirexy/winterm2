"""Unit tests for session management core module."""

import pytest
from unittest.mock import MagicMock, patch
import uuid


class TestSessionManager:
    """Test SessionManager class."""

    def test_session_manager_init(self):
        """Test SessionManager initialization."""
        from wt2.core.session_handler import SessionManager

        manager = SessionManager()
        assert manager is not None
        assert manager._sessions == {}

    def test_create_session(self):
        """Test creating a new session."""
        from wt2.core.session_handler import SessionManager

        manager = SessionManager()
        session_id = manager.create_session()
        assert session_id is not None
        assert session_id in manager._sessions

    def test_get_session(self):
        """Test getting a session."""
        from wt2.core.session_handler import SessionManager

        manager = SessionManager()
        session_id = manager.create_session()
        session = manager.get_session(session_id)
        assert session is not None
        assert session["id"] == session_id

    def test_get_nonexistent_session(self):
        """Test getting a nonexistent session."""
        from wt2.core.session_handler import SessionManager

        manager = SessionManager()
        result = manager.get_session("nonexistent-id")
        assert result is None

    def test_update_session(self):
        """Test updating a session."""
        from wt2.core.session_handler import SessionManager

        manager = SessionManager()
        session_id = manager.create_session()
        result = manager.update_session(session_id, {"key": "value"})
        assert result["success"] is True
        assert manager.get_session(session_id)["key"] == "value"

    def test_delete_session(self):
        """Test deleting a session."""
        from wt2.core.session_handler import SessionManager

        manager = SessionManager()
        session_id = manager.create_session()
        result = manager.delete_session(session_id)
        assert result["success"] is True
        assert manager.get_session(session_id) is None

    def test_list_sessions(self):
        """Test listing all sessions."""
        from wt2.core.session_handler import SessionManager

        manager = SessionManager()
        manager.create_session()
        manager.create_session()
        sessions = manager.list_sessions()
        assert len(sessions) == 2

    def test_clear_all_sessions(self):
        """Test clearing all sessions."""
        from wt2.core.session_handler import SessionManager

        manager = SessionManager()
        manager.create_session()
        manager.create_session()
        manager.clear_all()
        assert len(manager._sessions) == 0


class TestSessionState:
    """Test SessionState class."""

    def test_session_state_init(self):
        """Test SessionState initialization."""
        from wt2.core.session_handler import SessionState, SessionStatus

        state = SessionState()
        assert state.status == SessionStatus.INITIALIZED
        assert state.window_id is None
        assert state.tabs == []

    def test_session_state_start(self):
        """Test starting a session state."""
        from wt2.core.session_handler import SessionState, SessionStatus

        state = SessionState()
        state.start(window_id=1)
        assert state.status == SessionStatus.ACTIVE
        assert state.window_id == 1

    def test_session_state_close(self):
        """Test closing a session state."""
        from wt2.core.session_handler import SessionState, SessionStatus

        state = SessionState()
        state.start(window_id=1)
        state.close()
        assert state.status == SessionStatus.CLOSED

    def test_session_state_add_tab(self):
        """Test adding a tab to session state."""
        from wt2.core.session_handler import SessionState

        state = SessionState()
        state.add_tab({"id": 1, "name": "Tab 1"})
        assert len(state.tabs) == 1
        assert state.tabs[0]["name"] == "Tab 1"

    def test_session_state_remove_tab(self):
        """Test removing a tab from session state."""
        from wt2.core.session_handler import SessionState

        state = SessionState()
        state.add_tab({"id": 1, "name": "Tab 1"})
        state.remove_tab(1)
        assert len(state.tabs) == 0
