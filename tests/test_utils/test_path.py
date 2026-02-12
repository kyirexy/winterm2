"""Unit tests for path conversion utilities."""

import pytest
from unittest.mock import patch


class TestWindowsToWSL:
    """Test windows_to_wsl conversion."""

    def test_basic_drive_path(self):
        """Test converting basic Windows drive path."""
        from wt2.utils.path import windows_to_wsl

        result = windows_to_wsl("C:\\Users\\test")
        assert result == "/mnt/c/Users/test"

    def test_lowercase_drive(self):
        """Test converting with lowercase drive letter."""
        from wt2.utils.path import windows_to_wsl

        result = windows_to_wsl("c:\\Users\\test")
        assert result == "/mnt/c/Users/test"

    def test_empty_path(self):
        """Test converting empty path."""
        from wt2.utils.path import windows_to_wsl

        assert windows_to_wsl("") == ""
        assert windows_to_wsl(None) is None

    def test_unc_wsl_path(self):
        """Test converting WSL UNC path."""
        from wt2.utils.path import windows_to_wsl

        result = windows_to_wsl("\\\\wsl$\\Ubuntu\\home")
        assert "/mnt/" in result

    def test_relative_path(self):
        """Test converting relative path (unchanged)."""
        from wt2.utils.path import windows_to_wsl

        result = windows_to_wsl("Users\\test\\file.txt")
        assert "mnt" not in result


class TestWSLToWindows:
    """Test wsl_to_windows conversion."""

    def test_mnt_drive_path(self):
        """Test converting /mnt/d path."""
        from wt2.utils.path import wsl_to_windows

        result = wsl_to_windows("/mnt/d/foo/bar")
        assert result == "D:\\foo\\bar"

    def test_mnt_uppercase_drive(self):
        """Test /mnt with uppercase drive."""
        from wt2.utils.path import wsl_to_windows

        result = wsl_to_windows("/mnt/D/Foo/Bar")
        assert result == "D:\\Foo\\Bar"

    def test_wsl_distro_path(self):
        """Test converting WSL distribution path."""
        from wt2.utils.path import wsl_to_windows

        result = wsl_to_windows("/home/user/docs")
        assert "\\\\wsl$" in result
        assert "home" in result

    def test_empty_path(self):
        """Test converting empty path."""
        from wt2.utils.path import wsl_to_windows

        assert wsl_to_windows("") == ""
        assert wsl_to_windows(None) is None


class TestPathDetection:
    """Test path type detection."""

    def test_is_windows_path_drive(self):
        """Test detecting Windows path with drive letter."""
        from wt2.utils.path import is_windows_path

        assert is_windows_path("C:\\Users\\test") is True
        assert is_windows_path("d:\\Folder") is True

    def test_is_windows_path_unc(self):
        """Test detecting Windows UNC path."""
        from wt2.utils.path import is_windows_path

        assert is_windows_path("\\\\server\\share") is True

    def test_is_windows_path_false(self):
        """Test detecting non-Windows path."""
        from wt2.utils.path import is_windows_path

        assert is_windows_path("/home/user") is False
        assert is_windows_path("") is False

    def test_is_wsl_path(self):
        """Test detecting WSL path."""
        from wt2.utils.path import is_wsl_path

        assert is_wsl_path("/home/user") is True
        assert is_wsl_path("/mnt/c/Users") is True

    def test_is_wsl_path_false(self):
        """Test detecting non-WSL path."""
        from wt2.utils.path import is_wsl_path

        assert is_wsl_path("C:\\Users") is False
        assert is_wsl_path("") is False


class TestPathNormalization:
    """Test path normalization."""

    def test_normalize_to_wsl(self):
        """Test normalizing to WSL format."""
        from wt2.utils.path import normalize_path

        result = normalize_path("C:\\Users\\Test", prefer_wsl=True)
        assert result == "/mnt/c/Users/Test"

    def test_normalize_to_windows(self):
        """Test normalizing to Windows format."""
        from wt2.utils.path import normalize_path

        result = normalize_path("/home/user", prefer_wsl=False)
        assert "\\\\wsl$" in result

    def test_normalize_empty(self):
        """Test normalizing empty path."""
        from wt2.utils.path import normalize_path

        assert normalize_path("") == ""


class TestConvertPath:
    """Test convert_path function."""

    def test_convert_to_wsl(self):
        """Test converting path to WSL."""
        from wt2.utils.path import convert_path

        result = convert_path("D:\\Projects", to_wsl=True)
        assert result == "/mnt/d/Projects"

    def test_convert_to_windows(self):
        """Test converting path to Windows."""
        from wt2.utils.path import convert_path

        result = convert_path("/home/user", to_wsl=False)
        assert "\\\\wsl$" in result

    def test_convert_empty(self):
        """Test converting empty path."""
        from wt2.utils.path import convert_path

        assert convert_path("", to_wsl=True) == ""
        assert convert_path("", to_wsl=False) == ""


class TestWSLHelpers:
    """Test WSL helper functions."""

    def test_detect_wsl_distro(self):
        """Test detecting WSL distribution."""
        from wt2.utils.path import detect_wsl_distro

        # Returns empty string if WSL not available
        result = detect_wsl_distro()
        assert isinstance(result, str)

    def test_get_wsl_home_distro(self):
        """Test getting WSL home directory path."""
        from wt2.utils.path import get_wsl_home_distro

        result = get_wsl_home_distro()
        assert isinstance(result, str)
