"""Unit tests for session commands."""

import pytest
from unittest.mock import MagicMock, patch
import tempfile
import yaml


class TestSessionCommands:
    """Test session command functions."""

    def test_start_session_defaults(self):
        """Test starting session with defaults."""
        from wt2.commands.session import start_session

        with patch("wt2.core.connection.ConnectEx") as mock_connect:
            mock_conn = MagicMock()
            mock_connect.return_value = mock_conn
            mock_conn.SendMessage.return_value = {"success": True}

            result = start_session()
            assert result["success"] is True

    def test_start_session_with_profile(self):
        """Test starting session with profile."""
        from wt2.commands.session import start_session

        with patch("wt2.core.connection.ConnectEx") as mock_connect:
            mock_conn = MagicMock()
            mock_connect.return_value = mock_conn
            mock_conn.SendMessage.return_value = {"success": True}

            result = start_session(profile="PowerShell")
            assert result["success"] is True

    def test_start_session_with_custom_settings(self):
        """Test starting session with custom window settings."""
        from wt2.commands.session import start_session

        with patch("wt2.core.connection.ConnectEx") as mock_connect:
            mock_conn = MagicMock()
            mock_connect.return_value = mock_conn
            mock_conn.SendMessage.return_value = {"success": True}

            result = start_session(
                profile="Ubuntu",
                window_size=[120, 40],
                title="Dev Environment"
            )
            assert result["success"] is True

    def test_load_session_from_file(self):
        """Test loading session from config file."""
        from wt2.commands.session import load_session

        config_content = {
            "version": "1.0",
            "profiles": {
                "dev": {
                    "default_shell": "PowerShell",
                    "tabs": [
                        {"name": "Main", "profile": "PowerShell"}
                    ]
                }
            }
        }

        with tempfile.NamedTemporaryFile(mode='w', suffix='.yaml', delete=False) as f:
            yaml.dump(config_content, f)
            config_path = f.name

        try:
            with patch("wt2.core.connection.ConnectEx") as mock_connect:
                mock_conn = MagicMock()
                mock_connect.return_value = mock_conn
                mock_conn.SendMessage.return_value = {"success": True}

                result = load_session(config_path, profile="dev")
                assert result["success"] is True
        finally:
            import os
            os.unlink(config_path)

    def test_load_session_nonexistent_file(self):
        """Test loading session from nonexistent file."""
        from wt2.commands.session import load_session

        result = load_session("/nonexistent/path/config.yaml", profile="dev")
        assert result["success"] is False
        assert "error" in result

    def test_save_session(self):
        """Test saving current session state."""
        from wt2.commands.session import save_session

        with tempfile.NamedTemporaryFile(mode='w', suffix='.yaml', delete=False) as f:
            config_path = f.name

        try:
            with patch("wt2.core.connection.ConnectEx") as mock_connect:
                mock_conn = MagicMock()
                mock_connect.return_value = mock_conn
                mock_conn.SendMessage.return_value = {
                    "tabs": [
                        {"name": "Tab 1", "profile": "PowerShell"}
                    ]
                }

                result = save_session(config_path)
                assert result["success"] is True
                assert result["file"] == config_path
        finally:
            import os
            if os.path.exists(config_path):
                os.unlink(config_path)

    def test_export_session(self):
        """Test exporting session to file."""
        from wt2.commands.session import export_session

        with tempfile.NamedTemporaryFile(mode='w', suffix='.yaml', delete=False) as f:
            config_path = f.name

        try:
            with patch("wt2.core.connection.ConnectEx") as mock_connect:
                mock_conn = MagicMock()
                mock_connect.return_value = mock_conn
                mock_conn.SendMessage.return_value = {"success": True}

                result = export_session(config_path, format="yaml")
                assert result["success"] is True
        finally:
            import os
            if os.path.exists(config_path):
                os.unlink(config_path)

    def test_start_session_error_handling(self):
        """Test start session error handling."""
        from wt2.commands.session import start_session

        with patch("wt2.core.connection.ConnectEx") as mock_connect:
            mock_connect.side_effect = Exception("Connection failed")

            result = start_session()
            assert result["success"] is False
            assert "error" in result

    def test_run_workflow(self):
        """Test running a workflow."""
        from wt2.commands.session import run_workflow

        workflow = {
            "description": "Test workflow",
            "steps": [
                {"run_command": "echo step1"},
                {"run_command": "echo step2"}
            ]
        }

        with patch("wt2.core.connection.ConnectEx") as mock_connect:
            mock_conn = MagicMock()
            mock_connect.return_value = mock_conn
            mock_conn.SendMessage.return_value = {"success": True}

            result = run_workflow(workflow)
            assert result["success"] is True
            assert result["steps_completed"] == 2
