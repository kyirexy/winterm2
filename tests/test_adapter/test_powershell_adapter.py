"""Unit tests for PowerShell adapter."""

import pytest
from unittest.mock import MagicMock, patch


class TestPowerShellAdapterSpecific:
    """Additional tests for PowerShell adapter functionality."""

    def test_powershell_version_detection(self):
        """Test PowerShell version detection."""
        from wt2.adapters.powershell_adapter import PowerShellAdapter

        adapter = PowerShellAdapter()
        with patch("wt2.core.connection.ConnectEx") as mock:
            mock_conn = MagicMock()
            mock.return_value = mock_conn
            mock_conn.SendMessage.return_value = {"version": "7.4.0"}

            version = adapter.get_version()
            assert version == "7.4.0"

    def test_powershell_profile_loading(self):
        """Test PowerShell profile loading."""
        from wt2.adapters.powershell_adapter import PowerShellAdapter

        adapter = PowerShellAdapter()
        with patch("wt2.core.connection.ConnectEx") as mock:
            mock_conn = MagicMock()
            mock.return_value = mock_conn
            mock_conn.SendMessage.return_value = {"success": True}

            result = adapter.load_profile("Microsoft.PowerShell_profile.ps1")
            assert result["success"] is True

    def test_powershell_module_import(self):
        """Test importing PowerShell modules."""
        from wt2.adapters.powershell_adapter import PowerShellAdapter

        adapter = PowerShellAdapter()
        with patch("wt2.core.connection.ConnectEx") as mock:
            mock_conn = MagicMock()
            mock.return_value = mock_conn
            mock_conn.SendMessage.return_value = {"success": True}

            result = adapter.import_module("Az")
            assert result["success"] is True

    def test_powershell_environment_variable(self):
        """Test getting environment variable."""
        from wt2.adapters.powershell_adapter import PowerShellAdapter

        adapter = PowerShellAdapter()
        with patch("wt2.core.connection.ConnectEx") as mock:
            mock_conn = MagicMock()
            mock.return_value = mock_conn
            mock_conn.SendMessage.return_value = {"value": "C:\\Users\\Test"}

            result = adapter.get_env("USERPROFILE")
            assert result["value"] == "C:\\Users\\Test"

    def test_powershell_set_environment_variable(self):
        """Test setting environment variable."""
        from wt2.adapters.powershell_adapter import PowerShellAdapter

        adapter = PowerShellAdapter()
        with patch("wt2.core.connection.ConnectEx") as mock:
            mock_conn = MagicMock()
            mock.return_value = mock_conn
            mock_conn.SendMessage.return_value = {"success": True}

            result = adapter.set_env("TEST_VAR", "test_value")
            assert result["success"] is True

    def test_powershell_alias_management(self):
        """Test managing aliases."""
        from wt2.adapters.powershell_adapter import PowerShellAdapter

        adapter = PowerShellAdapter()
        with patch("wt2.core.connection.ConnectEx") as mock:
            mock_conn = MagicMock()
            mock.return_value = mock_conn
            mock_conn.SendMessage.return_value = {"success": True}

            result = adapter.new_alias("ll", "Get-ChildItem")
            assert result["success"] is True

    def test_powershell_error_handling(self):
        """Test PowerShell error handling."""
        from wt2.adapters.powershell_adapter import PowerShellAdapter

        adapter = PowerShellAdapter()
        with patch("wt2.core.connection.ConnectEx") as mock:
            mock_conn = MagicMock()
            mock.return_value = mock_conn
            mock_conn.SendMessage.return_value = {"error": "Command not found"}

            result = adapter.execute_command("Invalid-Command-12345")
            assert result["success"] is False
            assert "error" in result

    def test_powershell_multi_command(self):
        """Test executing multiple commands."""
        from wt2.adapters.powershell_adapter import PowerShellAdapter

        adapter = PowerShellAdapter()
        with patch("wt2.core.connection.ConnectEx") as mock:
            mock_conn = MagicMock()
            mock.return_value = mock_conn
            mock_conn.SendMessage.return_value = {"success": True}

            commands = [
                "$x = 1",
                "$y = 2",
                "$x + $y"
            ]
            result = adapter.execute_multi(commands)
            assert result["success"] is True
