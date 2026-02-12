"""Unit tests for terminal adapter module."""

import pytest
from unittest.mock import MagicMock, patch


class TestTerminalAdapter:
    """Test TerminalAdapter base class."""

    def test_adapter_init(self):
        """Test adapter initialization."""
        from wt2.adapters.terminal_adapter import TerminalAdapter

        adapter = TerminalAdapter()
        assert adapter is not None

    def test_execute_command_not_implemented(self):
        """Test that execute_command raises NotImplementedError."""
        from wt2.adapters.terminal_adapter import TerminalAdapter

        adapter = TerminalAdapter()
        with pytest.raises(NotImplementedError):
            adapter.execute_command("echo test")

    def test_get_prompt_not_implemented(self):
        """Test that get_prompt raises NotImplementedError."""
        from wt2.adapters.terminal_adapter import TerminalAdapter

        adapter = TerminalAdapter()
        with pytest.raises(NotImplementedError):
            adapter.get_prompt()

    def test_change_directory_not_implemented(self):
        """Test that change_directory raises NotImplementedError."""
        from wt2.adapters.terminal_adapter import TerminalAdapter

        adapter = TerminalAdapter()
        with pytest.raises(NotImplementedError):
            adapter.change_directory("/home")


class TestAdapterProperties:
    """Test adapter default properties."""

    def test_adapter_properties(self):
        """Test adapter default properties."""
        from wt2.adapters.terminal_adapter import TerminalAdapter

        adapter = TerminalAdapter()
        assert adapter.name == "base"
        assert adapter.supports_colors is True


class TestPowerShellAdapter:
    """Test PowerShell-specific adapter."""

    def test_adapter_init(self):
        """Test PowerShell adapter initialization."""
        from wt2.adapters.powershell_adapter import PowerShellAdapter

        adapter = PowerShellAdapter()
        assert adapter.name == "powershell"

    def test_execute_command(self):
        """Test executing a command in PowerShell."""
        from wt2.adapters.powershell_adapter import PowerShellAdapter

        adapter = PowerShellAdapter()
        with patch("wt2.core.connection.ConnectEx") as mock:
            mock_conn = MagicMock()
            mock.return_value = mock_conn
            mock_conn.SendMessage.return_value = {"success": True}

            result = adapter.execute_command("Get-Process")
            assert result["success"] is True

    def test_get_prompt(self):
        """Test getting PowerShell prompt."""
        from wt2.adapters.powershell_adapter import PowerShellAdapter

        adapter = PowerShellAdapter()
        with patch("wt2.core.connection.ConnectEx") as mock:
            mock_conn = MagicMock()
            mock.return_value = mock_conn
            mock_conn.SendMessage.return_value = {"prompt": "PS C:\\> "}

            result = adapter.get_prompt()
            assert result is not None

    def test_change_directory(self):
        """Test changing directory in PowerShell."""
        from wt2.adapters.powershell_adapter import PowerShellAdapter

        adapter = PowerShellAdapter()
        with patch("wt2.core.connection.ConnectEx") as mock:
            mock_conn = MagicMock()
            mock.return_value = mock_conn
            mock_conn.SendMessage.return_value = {"success": True}

            result = adapter.change_directory("C:\\Users\\Test")
            assert result["success"] is True

    def test_encode_command(self):
        """Test PowerShell command encoding."""
        from wt2.adapters.powershell_adapter import PowerShellAdapter

        adapter = PowerShellAdapter()
        # Test that command is properly encoded for PowerShell
        encoded = adapter._encode_command("echo test")
        assert encoded is not None


class TestWSLAdapter:
    """Test WSL-specific adapter."""

    def test_adapter_init(self):
        """Test WSL adapter initialization."""
        from wt2.adapters.wsl_adapter import WSLAdapter

        adapter = WSLAdapter()
        assert adapter.name == "wsl"

    def test_execute_command(self):
        """Test executing a command in WSL."""
        from wt2.adapters.wsl_adapter import WSLAdapter

        adapter = WSLAdapter()
        with patch("wt2.core.connection.ConnectEx") as mock:
            mock_conn = MagicMock()
            mock.return_value = mock_conn
            mock_conn.SendMessage.return_value = {"success": True}

            result = adapter.execute_command("ls -la")
            assert result["success"] is True

    def test_get_prompt(self):
        """Test getting WSL prompt."""
        from wt2.adapters.wsl_adapter import WSLAdapter

        adapter = WSLAdapter()
        with patch("wt2.core.connection.ConnectEx") as mock:
            mock_conn = MagicMock()
            mock.return_value = mock_conn
            mock_conn.SendMessage.return_value = {"prompt": "user@host:~$ "}

            result = adapter.get_prompt()
            assert result is not None

    def test_change_directory(self):
        """Test changing directory in WSL."""
        from wt2.adapters.wsl_adapter import WSLAdapter

        adapter = WSLAdapter()
        with patch("wt2.core.connection.ConnectEx") as mock:
            mock_conn = MagicMock()
            mock.return_value = mock_conn
            mock_conn.SendMessage.return_value = {"success": True}

            result = adapter.change_directory("/home/user")
            assert result["success"] is True

    def test_convert_windows_path(self):
        """Test converting Windows path to WSL path."""
        from wt2.adapters.wsl_adapter import WSLAdapter

        adapter = WSLAdapter()
        wsl_path = adapter._convert_windows_path("C:\\Users\\Test")
        assert "/mnt/c/Users/Test" in wsl_path or wsl_path == "/c/Users/Test"

    def test_execute_windows_command(self):
        """Test executing Windows command from WSL."""
        from wt2.adapters.wsl_adapter import WSLAdapter

        adapter = WSLAdapter()
        with patch("wt2.core.connection.ConnectEx") as mock:
            mock_conn = MagicMock()
            mock.return_value = mock_conn
            mock_conn.SendMessage.return_value = {"success": True}

            result = adapter.execute_windows_command("notepad.exe")
            assert result["success"] is True
