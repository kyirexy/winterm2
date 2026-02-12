"""Unit tests for window commands."""

import pytest
from unittest.mock import MagicMock, patch


class TestWindowCommands:
    """Test window command functions."""

    def test_new_window_defaults(self):
        """Test new window with default settings."""
        from wt2.commands.window import new_window

        with patch("wt2.core.connection.ConnectEx") as mock_connect:
            mock_conn = MagicMock()
            mock_connect.return_value = mock_conn
            mock_conn.SendMessage.return_value = {"success": True}

            result = new_window()
            assert result["success"] is True

    def test_new_window_with_profile(self):
        """Test new window with specific profile."""
        from wt2.commands.window import new_window

        with patch("wt2.core.connection.ConnectEx") as mock_connect:
            mock_conn = MagicMock()
            mock_connect.return_value = mock_conn
            mock_conn.SendMessage.return_value = {"success": True}

            result = new_window(profile="PowerShell")
            assert result["success"] is True
            # Verify the profile was set correctly
            call_args = mock_conn.SendMessage.call_args
            assert "PowerShell" in str(call_args)

    def test_new_window_with_size(self):
        """Test new window with specific size."""
        from wt2.commands.window import new_window

        with patch("wt2.core.connection.ConnectEx") as mock_connect:
            mock_conn = MagicMock()
            mock_connect.return_value = mock_conn
            mock_conn.SendMessage.return_value = {"success": True}

            result = new_window(size=[120, 40])
            assert result["success"] is True

    def test_new_window_with_startup_dir(self):
        """Test new window with startup directory."""
        from wt2.commands.window import new_window

        with patch("wt2.core.connection.ConnectEx") as mock_connect:
            mock_conn = MagicMock()
            mock_connect.return_value = mock_conn
            mock_conn.SendMessage.return_value = {"success": True}

            result = new_window(startup_dir="C:\\Users\\test")
            assert result["success"] is True

    def test_new_window_error_handling(self):
        """Test new window error handling."""
        from wt2.commands.window import new_window

        with patch("wt2.core.connection.ConnectEx") as mock_connect:
            mock_connect.side_effect = Exception("Connection failed")

            result = new_window()
            assert result["success"] is False
            assert "error" in result

    def test_close_window(self):
        """Test closing a window."""
        from wt2.commands.window import close_window

        with patch("wt2.core.connection.ConnectEx") as mock_connect:
            mock_conn = MagicMock()
            mock_connect.return_value = mock_conn
            mock_conn.SendMessage.return_value = {"success": True}

            result = close_window(window_id=1)
            assert result["success"] is True

    def test_focus_window(self):
        """Test focusing a window."""
        from wt2.commands.window import focus_window

        with patch("wt2.core.connection.ConnectEx") as mock_connect:
            mock_conn = MagicMock()
            mock_connect.return_value = mock_conn
            mock_conn.SendMessage.return_value = {"success": True}

            result = focus_window(window_id=1)
            assert result["success"] is True
