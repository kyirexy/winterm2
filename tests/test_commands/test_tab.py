"""Unit tests for tab commands."""

import pytest
from unittest.mock import MagicMock, patch


class TestTabCommands:
    """Test tab command functions."""

    def test_new_tab_defaults(self):
        """Test new tab with default settings."""
        from wt2.commands.tab import new_tab

        with patch("wt2.core.connection.ConnectEx") as mock_connect:
            mock_conn = MagicMock()
            mock_connect.return_value = mock_conn
            mock_conn.SendMessage.return_value = {"success": True}

            result = new_tab()
            assert result["success"] is True

    def test_new_tab_with_profile(self):
        """Test new tab with specific profile."""
        from wt2.commands.tab import new_tab

        with patch("wt2.core.connection.ConnectEx") as mock_connect:
            mock_conn = MagicMock()
            mock_connect.return_value = mock_conn
            mock_conn.SendMessage.return_value = {"success": True}

            result = new_tab(profile="Ubuntu")
            assert result["success"] is True

    def test_new_tab_with_title(self):
        """Test new tab with custom title."""
        from wt2.commands.tab import new_tab

        with patch("wt2.core.connection.ConnectEx") as mock_connect:
            mock_conn = MagicMock()
            mock_connect.return_value = mock_conn
            mock_conn.SendMessage.return_value = {"success": True}

            result = new_tab(title="My Tab")
            assert result["success"] is True

    def test_new_tab_with_command(self):
        """Test new tab with initial command."""
        from wt2.commands.tab import new_tab

        with patch("wt2.core.connection.ConnectEx") as mock_connect:
            mock_conn = MagicMock()
            mock_connect.return_value = mock_conn
            mock_conn.SendMessage.return_value = {"success": True}

            result = new_tab(command="cd C:\\Users\\test")
            assert result["success"] is True

    def test_new_tab_in_specific_window(self):
        """Test creating tab in specific window."""
        from wt2.commands.tab import new_tab

        with patch("wt2.core.connection.ConnectEx") as mock_connect:
            mock_conn = MagicMock()
            mock_connect.return_value = mock_conn
            mock_conn.SendMessage.return_value = {"success": True}

            result = new_tab(window_id=2, profile="PowerShell")
            assert result["success"] is True

    def test_close_tab(self):
        """Test closing a tab."""
        from wt2.commands.tab import close_tab

        with patch("wt2.core.connection.ConnectEx") as mock_connect:
            mock_conn = MagicMock()
            mock_connect.return_value = mock_conn
            mock_conn.SendMessage.return_value = {"success": True}

            result = close_tab(tab_id=1)
            assert result["success"] is True

    def test_focus_tab(self):
        """Test focusing a tab."""
        from wt2.commands.tab import focus_tab

        with patch("wt2.core.connection.ConnectEx") as mock_connect:
            mock_conn = MagicMock()
            mock_connect.return_value = mock_conn
            mock_conn.SendMessage.return_value = {"success": True}

            result = focus_tab(tab_id=1)
            assert result["success"] is True

    def test_rename_tab(self):
        """Test renaming a tab."""
        from wt2.commands.tab import rename_tab

        with patch("wt2.core.connection.ConnectEx") as mock_connect:
            mock_conn = MagicMock()
            mock_connect.return_value = mock_conn
            mock_conn.SendMessage.return_value = {"success": True}

            result = rename_tab(tab_id=1, title="New Name")
            assert result["success"] is True

    def test_get_tabs(self):
        """Test getting list of tabs."""
        from wt2.commands.tab import get_tabs

        with patch("wt2.core.connection.ConnectEx") as mock_connect:
            mock_conn = MagicMock()
            mock_connect.return_value = mock_conn
            mock_conn.SendMessage.return_value = {
                "tabs": [
                    {"id": 1, "title": "Tab 1"},
                    {"id": 2, "title": "Tab 2"}
                ]
            }

            result = get_tabs(window_id=1)
            assert "tabs" in result
            assert len(result["tabs"]) == 2

    def test_new_tab_error_handling(self):
        """Test new tab error handling."""
        from wt2.commands.tab import new_tab

        with patch("wt2.core.connection.ConnectEx") as mock_connect:
            mock_connect.side_effect = Exception("Connection failed")

            result = new_tab()
            assert result["success"] is False
            assert "error" in result
