"""Unit tests for configuration utilities."""

import pytest
import tempfile
import os
import yaml


class TestConfigLoader:
    """Test configuration file loading."""

    def test_load_valid_yaml(self):
        """Test loading a valid YAML configuration."""
        from wt2.utils.config import ConfigLoader

        config_content = {
            "version": "1.0",
            "general": {
                "default_shell": "PowerShell"
            },
            "profiles": []
        }

        with tempfile.NamedTemporaryFile(mode='w', suffix='.yaml', delete=False) as f:
            yaml.dump(config_content, f)
            config_path = f.name

        try:
            loader = ConfigLoader()
            result = loader.load(config_path)
            assert result.version == "1.0"
            assert result.general.default_shell == "PowerShell"
        finally:
            os.unlink(config_path)

    def test_load_nonexistent_file(self):
        """Test loading a nonexistent file raises error."""
        from wt2.utils.config import ConfigLoader
        from wt2.core.exceptions import ConfigError

        loader = ConfigLoader()
        with pytest.raises(ConfigError):
            loader.load("/nonexistent/path/config.yaml", ignore_errors=False)

    def test_load_with_ignore_errors(self):
        """Test loading with ignore_errors returns default config."""
        from wt2.utils.config import ConfigLoader

        loader = ConfigLoader()
        result = loader.load("/nonexistent/path/config.yaml", ignore_errors=True)
        assert result is not None
        assert result.version == "1.0"

    def test_load_empty_file(self):
        """Test loading an empty configuration file."""
        from wt2.utils.config import ConfigLoader

        with tempfile.NamedTemporaryFile(mode='w', suffix='.yaml', delete=False) as f:
            f.write("")
            config_path = f.name

        try:
            loader = ConfigLoader()
            result = loader.load(config_path)
            assert result is not None
        finally:
            os.unlink(config_path)

    def test_find_config_file(self):
        """Test finding configuration file in standard locations."""
        from wt2.utils.config import ConfigLoader

        loader = ConfigLoader()
        # Should return None if no config exists
        result = loader.find_config_file()
        # Result is None if no config found, which is valid
        assert result is None or result.exists()


class TestWT2Config:
    """Test WT2Config dataclass."""

    def test_default_config(self):
        """Test creating default configuration."""
        from wt2.utils.config import WT2Config

        config = WT2Config()
        assert config.version == "1.0"
        assert config.general.default_shell == "powershell"
        assert len(config.profiles) == 0

    def test_config_from_dict(self):
        """Test creating config from dictionary."""
        from wt2.utils.config import WT2Config

        data = {
            "version": "1.0",
            "general": {
                "default_shell": "Ubuntu",
                "verbose_output": True
            },
            "profiles": [
                {
                    "name": "dev",
                    "commandline": "powershell.exe",
                    "starting_directory": "C:\\Projects"
                }
            ]
        }

        config = WT2Config.from_dict(data)
        assert config.version == "1.0"
        assert config.general.default_shell == "Ubuntu"
        assert config.general.verbose_output is True
        assert len(config.profiles) == 1
        assert config.profiles[0].name == "dev"


class TestConfigSaving:
    """Test configuration saving."""

    def test_save_config(self):
        """Test saving configuration to file."""
        from wt2.utils.config import WT2Config, ConfigLoader

        config = WT2Config()
        config.general.default_shell = "PowerShell"

        with tempfile.TemporaryDirectory() as tmpdir:
            save_path = os.path.join(tmpdir, "test.yaml")
            loader = ConfigLoader()
            result = loader.save(config, save_path)

            assert os.path.exists(save_path)

            # Verify saved content
            with open(save_path, "r") as f:
                saved = yaml.safe_load(f)
            assert saved["general"]["default_shell"] == "PowerShell"


class TestParseConfig:
    """Test parse_config convenience function."""

    def test_parse_config_valid(self):
        """Test parsing valid config."""
        from wt2.utils.config import parse_config

        with tempfile.NamedTemporaryFile(mode='w', suffix='.yaml', delete=False) as f:
            yaml.dump({"version": "1.0"}, f)
            config_path = f.name

        try:
            result = parse_config(config_path, ignore_errors=True)
            assert result is not None
            assert result.version == "1.0"
        finally:
            os.unlink(config_path)

    def test_parse_config_invalid(self):
        """Test parsing invalid config with ignore_errors."""
        from wt2.utils.config import parse_config

        result = parse_config("/nonexistent.yaml", ignore_errors=True)
        assert result is not None
        assert result.version == "1.0"
