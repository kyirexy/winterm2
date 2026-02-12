"""Unit tests for terminal API core module."""

import pytest
from unittest.mock import MagicMock, patch
import json


class TestTerminalConnection:
    """Test TerminalConnection class."""

    def test_connection_init(self):
        """Test TerminalConnection initialization."""
        from wt2.core.connection import TerminalConnection

        conn = TerminalConnection()
        assert conn is not None
        assert conn._connected is False

    def test_connect(self):
        """Test establishing connection."""
        from wt2.core.connection import TerminalConnection

        conn = TerminalConnection()
        with patch("wt2.core.connection.ConnectEx") as mock:
            mock.return_value = MagicMock()
            result = conn.connect()
            assert result is True
            assert conn._connected is True

    def test_disconnect(self):
        """Test disconnecting."""
        from wt2.core.connection import TerminalConnection

        conn = TerminalConnection()
        with patch("wt2.core.connection.ConnectEx") as mock:
            mock.return_value = MagicMock()
            conn.connect()
            conn.disconnect()
            assert conn._connected is False

    def test_send_message(self):
        """Test sending a message."""
        from wt2.core.connection import TerminalConnection

        mock_com = MagicMock()
        mock_com.SendMessage.return_value = json.dumps({"success": True})

        conn = TerminalConnection()
        conn._connection = mock_com

        result = conn.send_message({"action": "test"})
        assert result["success"] is True

    def test_send_message_disconnected(self):
        """Test sending message when disconnected."""
        from wt2.core.connection import TerminalConnection

        conn = TerminalConnection()
        result = conn.send_message({"action": "test"})
        assert result["success"] is False
        assert "error" in result

    def test_get_terminal_info(self):
        """Test getting terminal information."""
        from wt2.core.connection import TerminalConnection

        mock_com = MagicMock()
        mock_com.SendMessage.return_value = json.dumps({
            "version": "1.18",
            "settings": {}
        })

        conn = TerminalConnection()
        conn._connection = mock_com

        result = conn.get_terminal_info()
        assert result["version"] == "1.18"

    def test_list_profiles(self):
        """Test listing profiles."""
        from wt2.core.connection import TerminalConnection

        mock_com = MagicMock()
        mock_com.SendMessage.return_value = json.dumps({
            "profiles": [
                {"name": "PowerShell", "guid": "..."},
                {"name": "Ubuntu", "guid": "..."}
            ]
        })

        conn = TerminalConnection()
        conn._connection = mock_com

        result = conn.list_profiles()
        assert "profiles" in result
        assert len(result["profiles"]) == 2


class TestTerminalAPI:
    """Test TerminalAPI class for high-level operations."""

    def test_api_init(self):
        """Test API initialization."""
        from wt2.core.connection import TerminalAPI

        api = TerminalAPI()
        assert api is not None

    def test_create_window(self):
        """Test creating a window via API."""
        from wt2.core.connection import TerminalAPI

        mock_conn = MagicMock()
        mock_conn.send_message.return_value = {"success": True, "id": 1}

        api = TerminalAPI()
        api._connection = mock_conn

        result = api.create_window(profile="PowerShell")
        assert result["success"] is True

    def test_create_tab(self):
        """Test creating a tab via API."""
        from wt2.core.connection import TerminalAPI

        mock_conn = MagicMock()
        mock_conn.send_message.return_value = {"success": True, "id": 1}

        api = TerminalAPI()
        api._connection = mock_conn

        result = api.create_tab(window_id=1, profile="PowerShell")
        assert result["success"] is True

    def test_execute_command(self):
        """Test executing a command via API."""
        from wt2.core.connection import TerminalAPI

        mock_conn = MagicMock()
        mock_conn.send_message.return_value = {"success": True}

        api = TerminalAPI()
        api._connection = mock_conn

        result = api.execute_command(tab_id=1, command="echo test")
        assert result["success"] is True

    def test_get_window_list(self):
        """Test getting list of windows."""
        from wt2.core.connection import TerminalAPI

        mock_conn = MagicMock()
        mock_conn.send_message.return_value = {
            "windows": [{"id": 1}, {"id": 2}]
        }

        api = TerminalAPI()
        api._connection = mock_conn

        result = api.get_window_list()
        assert "windows" in result
        assert len(result["windows"]) == 2

    def test_get_active_window(self):
        """Test getting active window."""
        from wt2.core.connection import TerminalAPI

        mock_conn = MagicMock()
        mock_conn.send_message.return_value = {"id": 1, "activeTab": 3}

        api = TerminalAPI()
        api._connection = mock_conn

        result = api.get_active_window()
        assert result["id"] == 1
