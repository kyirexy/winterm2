"""Pytest configuration and fixtures for winterm2 tests."""

import pytest
import sys
from pathlib import Path

# Add src directory to path for imports
src_path = Path(__file__).parent.parent / "src"
if src_path.exists():
    sys.path.insert(0, str(src_path))


@pytest.fixture
def mock_windows_terminal_api(mocker):
    """Mock Windows Terminal COM API calls."""
    mock_com = mocker.patch("wt2.core.connection.ConnectEx")
    mock_com.return_value = mocker.MagicMock()
    return mock_com


@pytest.fixture
def sample_config():
    """Sample configuration for testing."""
    return {
        "version": "1.0",
        "profiles": {
            "dev": {
                "default_shell": "PowerShell",
                "window": {
                    "profile": "PowerShell",
                    "size": [120, 40]
                },
                "tabs": [
                    {"name": "Server", "profile": "Ubuntu"}
                ]
            }
        }
    }


@pytest.fixture
def temp_config_file(tmp_path, sample_config):
    """Create a temporary config file."""
    import yaml
    config_path = tmp_path / "test.wt2rc.yaml"
    with open(config_path, "w") as f:
        yaml.dump(sample_config, f)
    return config_path


@pytest.fixture
def runner():
    """Create a CLI test runner."""
    from click.testing import CliRunner
    return CliRunner()
