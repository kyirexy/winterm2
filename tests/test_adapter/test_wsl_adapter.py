"""Unit tests for WSL adapter."""

import pytest
from unittest.mock import MagicMock, patch


class TestWSLAdapterSpecific:
    """Additional tests for WSL adapter functionality."""

    def test_wsl_distribution_list(self):
        """Test listing WSL distributions."""
        from wt2.adapters.wsl_adapter import WSLAdapter

        adapter = WSLAdapter()
        with patch("wt2.core.connection.ConnectEx") as mock:
            mock_conn = MagicMock()
            mock.return_value = mock_conn
            mock_conn.SendMessage.return_value = {
                "distros": [
                    {"name": "Ubuntu", "default": True},
                    {"name": "Debian", "default": False}
                ]
            }

            result = adapter.list_distributions()
            assert "distros" in result
            assert len(result["distros"]) == 2

    def test_wsl_set_default_distro(self):
        """Test setting default WSL distribution."""
        from wt2.adapters.wsl_adapter import WSLAdapter

        adapter = WSLAdapter()
        with patch("wt2.core.connection.ConnectEx") as mock:
            mock_conn = MagicMock()
            mock.return_value = mock_conn
            mock_conn.SendMessage.return_value = {"success": True}

            result = adapter.set_default_distro("Ubuntu")
            assert result["success"] is True

    def test_wsl_run_as_user(self):
        """Test running command as specific user."""
        from wt2.adapters.wsl_adapter import WSLAdapter

        adapter = WSLAdapter()
        with patch("wt2.core.connection.ConnectEx") as mock:
            mock_conn = MagicMock()
            mock.return_value = mock_conn
            mock_conn.SendMessage.return_value = {"success": True}

            result = adapter.run_as_user("root", "whoami")
            assert result["success"] is True

    def test_wsl_mount_points(self):
        """Test getting mount points."""
        from wt2.adapters.wsl_adapter import WSLAdapter

        adapter = WSLAdapter()
        with patch("wt2.core.connection.ConnectEx") as mock:
            mock_conn = MagicMock()
            mock.return_value = mock_conn
            mock_conn.SendMessage.return_value = {
                "mounts": [
                    {"source": "C:", "target": "/mnt/c"},
                    {"source": "D:", "target": "/mnt/d"}
                ]
            }

            result = adapter.get_mount_points()
            assert "mounts" in result

    def test_wsl_convert_path_edge_cases(self):
        """Test path conversion edge cases."""
        from wt2.adapters.wsl_adapter import WSLAdapter

        adapter = WSLAdapter()

        # Test empty path
        result = adapter._convert_windows_path("")
        assert result == ""

        # Test root path
        result = adapter._convert_windows_path("C:\\")
        assert "mnt/c" in result or result == "/c"

        # Test path with spaces
        result = adapter._convert_windows_path("C:\\Program Files")
        assert "Program" in result or "Files" in result

    def test_wsl_export_distro(self):
        """Test exporting WSL distribution."""
        from wt2.adapters.wsl_adapter import WSLAdapter

        adapter = WSLAdapter()
        with patch("wt2.core.connection.ConnectEx") as mock:
            mock_conn = MagicMock()
            mock.return_value = mock_conn
            mock_conn.SendMessage.return_value = {"success": True}

            result = adapter.export_distro("Ubuntu", "C:\\backup.tar")
            assert result["success"] is True

    def test_wsl_import_distro(self):
        """Test importing WSL distribution."""
        from wt2.adapters.wsl_adapter import WSLAdapter

        adapter = WSLAdapter()
        with patch("wt2.core.connection.ConnectEx") as mock:
            mock_conn = MagicMock()
            mock.return_value = mock_conn
            mock_conn.SendMessage.return_value = {"success": True}

            result = adapter.import_distro("Test", "C:\\test.tar", "C:\\test")
            assert result["success"] is True

    def test_wsl_version(self):
        """Test getting WSL version."""
        from wt2.adapters.wsl_adapter import WSLAdapter

        adapter = WSLAdapter()
        with patch("wt2.core.connection.ConnectEx") as mock:
            mock_conn = MagicMock()
            mock.return_value = mock_conn
            mock_conn.SendMessage.return_value = {"version": "2.0.0"}

            version = adapter.get_wsl_version()
            assert version == "2.0.0"

    def test_wsl_shutdown(self):
        """Test shutting down WSL."""
        from wt2.adapters.wsl_adapter import WSLAdapter

        adapter = WSLAdapter()
        with patch("wt2.core.connection.ConnectEx") as mock:
            mock_conn = MagicMock()
            mock.return_value = mock_conn
            mock_conn.SendMessage.return_value = {"success": True}

            result = adapter.shutdown()
            assert result["success"] is True

    def test_wsl_terminate_distro(self):
        """Test terminating a WSL distribution."""
        from wt2.adapters.wsl_adapter import WSLAdapter

        adapter = WSLAdapter()
        with patch("wt2.core.connection.ConnectEx") as mock:
            mock_conn = MagicMock()
            mock.return_value = mock_conn
            mock_conn.SendMessage.return_value = {"success": True}

            result = adapter.terminate_distro("Ubuntu")
            assert result["success"] is True
