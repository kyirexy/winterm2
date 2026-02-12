"""Unit tests for pane commands."""

import pytest
from unittest.mock import MagicMock, patch


class TestPaneCommands:
    """Test pane command functions."""

    def test_split_pane_defaults(self):
        """Test splitting pane with defaults."""
        from wt2.commands.pane import split_pane

        with patch("wt2.core.connection.ConnectEx") as mock_connect:
            mock_conn = MagicMock()
            mock_connect.return_value = mock_conn
            mock_conn.SendMessage.return_value = {"success": True}

            result = split_pane()
            assert result["success"] is True

    def test_split_pane_direction(self):
        """Test splitting pane in different directions."""
        from wt2.commands.pane import split_pane

        with patch("wt2.core.connection.ConnectEx") as mock_connect:
            mock_conn = MagicMock()
            mock_connect.return_value = mock_conn
            mock_conn.SendMessage.return_value = {"success": True}

            for direction in ["horizontal", "vertical", "left", "right", "up", "down"]:
                result = split_pane(direction=direction)
                assert result["success"] is True

    def test_split_pane_with_profile(self):
        """Test splitting pane with profile."""
        from wt2.commands.pane import split_pane

        with patch("wt2.core.connection.ConnectEx") as mock_connect:
            mock_conn = MagicMock()
            mock_connect.return_value = mock_conn
            mock_conn.SendMessage.return_value = {"success": True}

            result = split_pane(profile="PowerShell")
            assert result["success"] is True

    def test_split_pane_with_size(self):
        """Test splitting pane with size."""
        from wt2.commands.pane import split_pane

        with patch("wt2.core.connection.ConnectEx") as mock_connect:
            mock_conn = MagicMock()
            mock_connect.return_value = mock_conn
            mock_conn.SendMessage.return_value = {"success": True}

            result = split_pane(size=0.5)
            assert result["success"] is True

    def test_close_pane(self):
        """Test closing a pane."""
        from wt2.commands.pane import close_pane

        with patch("wt2.core.connection.ConnectEx") as mock_connect:
            mock_conn = MagicMock()
            mock_connect.return_value = mock_conn
            mock_conn.SendMessage.return_value = {"success": True}

            result = close_pane(pane_id=1)
            assert result["success"] is True

    def test_focus_pane(self):
        """Test focusing a pane."""
        from wt2.commands.pane import focus_pane

        with patch("wt2.core.connection.ConnectEx") as mock_connect:
            mock_conn = MagicMock()
            mock_connect.return_value = mock_conn
            mock_conn.SendMessage.return_value = {"success": True}

            result = focus_pane(pane_id=1)
            assert result["success"] is True

    def test_swap_pane(self):
        """Test swapping panes."""
        from wt2.commands.pane import swap_pane

        with patch("wt2.core.connection.ConnectEx") as mock_connect:
            mock_conn = MagicMock()
            mock_connect.return_value = mock_conn
            mock_conn.SendMessage.return_value = {"success": True}

            result = swap_pane(pane_id=1, target_pane_id=2)
            assert result["success"] is True

    def test_resize_pane(self):
        """Test resizing a pane."""
        from wt2.commands.pane import resize_pane

        with patch("wt2.core.connection.ConnectEx") as mock_connect:
            mock_conn = MagicMock()
            mock_connect.return_value = mock_conn
            mock_conn.SendMessage.return_value = {"success": True}

            result = resize_pane(pane_id=1, deltaX=5, deltaY=10)
            assert result["success"] is True

    def test_get_panes(self):
        """Test getting list of panes."""
        from wt2.commands.pane import get_panes

        with patch("wt2.core.connection.ConnectEx") as mock_connect:
            mock_conn = MagicMock()
            mock_connect.return_value = mock_conn
            mock_conn.SendMessage.return_value = {
                "panes": [
                    {"id": 1, "focused": True},
                    {"id": 2, "focused": False}
                ]
            }

            result = get_panes(tab_id=1)
            assert "panes" in result
            assert len(result["panes"]) == 2

    def test_split_pane_error_handling(self):
        """Test split pane error handling."""
        from wt2.commands.pane import split_pane

        with patch("wt2.core.connection.ConnectEx") as mock_connect:
            mock_connect.side_effect = Exception("Connection failed")

            result = split_pane()
            assert result["success"] is False
            assert "error" in result

    def test_split_pane_invalid_direction(self):
        """Test split pane with invalid direction."""
        from wt2.commands.pane import split_pane

        result = split_pane(direction="invalid")
        assert result["success"] is False
        assert "error" in result
