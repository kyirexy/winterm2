"""Unit tests for CLI entry point."""

import pytest
from click.testing import CliRunner


class TestCLI:
    """Test CLI entry point and basic commands."""

    def test_cli_help(self, runner):
        """Test CLI help command."""
        from wt2.cli import main

        result = runner.invoke(main, ["--help"])
        assert result.exit_code == 0
        assert "Windows Terminal" in result.output.lower() or "wt2" in result.output.lower()

    def test_cli_version(self, runner):
        """Test CLI version command."""
        from wt2.cli import main

        result = runner.invoke(main, ["--version"])
        assert result.exit_code == 0
        assert "0.1.0" in result.output

    def test_cli_no_args(self, runner):
        """Test CLI with no arguments shows help."""
        from wt2.cli import main

        result = runner.invoke(main, [])
        # Should show help or error gracefully
        assert result.exit_code in [0, 1]


class TestWindowCommands:
    """Test window-related commands."""

    def test_window_new_help(self, runner):
        """Test window new command help."""
        from wt2.cli import main

        result = runner.invoke(main, ["window", "--help"])
        assert result.exit_code == 0

    def test_window_new_command(self, runner, mocker):
        """Test creating a new window."""
        from wt2.cli import main

        mock_new_window = mocker.patch("wt2.commands.window.new_window")
        mock_new_window.return_value = {"success": True}

        result = runner.invoke(main, ["window", "new", "--profile", "PowerShell"])
        assert result.exit_code == 0

    def test_window_new_with_size(self, runner, mocker):
        """Test creating a new window with size."""
        from wt2.cli import main

        mock_new_window = mocker.patch("wt2.commands.window.new_window")
        mock_new_window.return_value = {"success": True}

        result = runner.invoke(main, ["window", "new", "--profile", "PowerShell", "--size", "120", "40"])
        assert result.exit_code == 0


class TestTabCommands:
    """Test tab-related commands."""

    def test_tab_help(self, runner):
        """Test tab command help."""
        from wt2.cli import main

        result = runner.invoke(main, ["tab", "--help"])
        assert result.exit_code == 0

    def test_tab_new_command(self, runner, mocker):
        """Test creating a new tab."""
        from wt2.cli import main

        mock_new_tab = mocker.patch("wt2.commands.tab.new_tab")
        mock_new_tab.return_value = {"success": True}

        result = runner.invoke(main, ["tab", "new", "--profile", "PowerShell"])
        assert result.exit_code == 0

    def test_tab_split_command(self, runner, mocker):
        """Test splitting a pane."""
        from wt2.cli import main

        mock_split = mocker.patch("wt2.commands.pane.split_pane")
        mock_split.return_value = {"success": True}

        result = runner.invoke(main, ["tab", "split", "--profile", "PowerShell", "--direction", "right"])
        assert result.exit_code == 0


class TestSessionCommands:
    """Test session management commands."""

    def test_session_help(self, runner):
        """Test session command help."""
        from wt2.cli import main

        result = runner.invoke(main, ["session", "--help"])
        assert result.exit_code == 0

    def test_session_start_command(self, runner, mocker):
        """Test starting a session."""
        from wt2.cli import main

        mock_session = mocker.patch("wt2.commands.session.start_session")
        mock_session.return_value = {"success": True}

        result = runner.invoke(main, ["session", "start", "--profile", "dev"])
        assert result.exit_code == 0

    def test_session_load_command(self, runner, mocker, temp_config_file):
        """Test loading a session from config."""
        from wt2.cli import main

        mock_load = mocker.patch("wt2.commands.session.load_session")
        mock_load.return_value = {"success": True}

        result = runner.invoke(main, ["session", "load", str(temp_config_file), "--profile", "dev"])
        assert result.exit_code == 0


class TestConfigCommands:
    """Test configuration commands."""

    def test_config_help(self, runner):
        """Test config command help."""
        from wt2.cli import main

        result = runner.invoke(main, ["config", "--help"])
        assert result.exit_code == 0

    def test_config_init_command(self, runner, mocker, tmp_path):
        """Test initializing a new config file."""
        from wt2.cli import main

        config_path = tmp_path / "new.wt2rc.yaml"

        result = runner.invoke(main, ["config", "init", str(config_path)])
        assert result.exit_code == 0
        assert config_path.exists()
