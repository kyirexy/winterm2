"""
YAML configuration parsing module.

Handles loading and parsing of ~/.wt2rc.yaml configuration files.
"""

from __future__ import annotations
import os
import yaml
from pathlib import Path
from typing import Any, Dict, List, Optional
from dataclasses import dataclass, field

from ..core.exceptions import ConfigError


# Default config file locations
CONFIG_FILE_NAMES = [
    ".wt2rc.yaml",
    ".wt2rc.yml",
    "wt2rc.yaml",
]
CONFIG_DIR_NAMES = [
    ".wt2",
    "winterm2",
]


@dataclass
class ProfileConfig:
    """Configuration for a terminal profile."""

    name: str
    commandline: Optional[str] = None
    starting_directory: Optional[str] = None
    icon: Optional[str] = None
    color_scheme: Optional[str] = None
    background: Optional[str] = None
    font: Optional[str] = None
    font_size: Optional[int] = None


@dataclass
class KeybindingConfig:
    """Configuration for a key binding."""

    keys: str
    action: str
    command: Optional[str] = None
    args: Optional[List[str]] = None


@dataclass
class ThemeConfig:
    """Configuration for a theme."""

    name: str
    background: str
    foreground: str
    cursor: Optional[str] = None
    selection: Optional[str] = None
    colors: Dict[str, str] = field(default_factory=dict)


@dataclass
class BroadcastConfig:
    """Configuration for broadcast settings."""

    enabled: bool = True
    escape_char: str = "\\"
    timeout: float = 5.0


@dataclass
class MonitorConfig:
    """Configuration for monitor settings."""

    follow: bool = False
    filter: Optional[str] = None
    highlight: bool = True
    auto_scroll: bool = True


@dataclass
class GeneralConfig:
    """General configuration settings."""

    default_shell: str = "powershell"
    default_profile: Optional[str] = None
    confirmation_prompt: bool = True
    verbose_output: bool = False
    max_history: int = 1000


@dataclass
class WT2Config:
    """
    Main configuration class.

    Attributes:
        version: Configuration version.
        general: General settings.
        profiles: Custom profiles.
        themes: Custom themes.
        keybindings: Custom keybindings.
        broadcast: Broadcast settings.
        monitor: Monitor settings.
    """

    version: str = "1.0"
    general: GeneralConfig = field(default_factory=GeneralConfig)
    profiles: List[ProfileConfig] = field(default_factory=list)
    themes: List[ThemeConfig] = field(default_factory=list)
    keybindings: List[KeybindingConfig] = field(default_factory=list)
    broadcast: BroadcastConfig = field(default_factory=BroadcastConfig)
    monitor: MonitorConfig = field(default_factory=MonitorConfig)

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "WT2Config":
        """
        Create configuration from a dictionary.

        Args:
            data: Configuration dictionary.

        Returns:
            WT2Config instance.
        """
        config = cls()

        # Parse general settings
        if "general" in data:
            general_data = data["general"]
            config.general = GeneralConfig(
                default_shell=general_data.get("default_shell", "powershell"),
                default_profile=general_data.get("default_profile"),
                confirmation_prompt=general_data.get("confirmation_prompt", True),
                verbose_output=general_data.get("verbose_output", False),
                max_history=general_data.get("max_history", 1000),
            )

        # Parse profiles
        if "profiles" in data:
            for profile_data in data["profiles"]:
                config.profiles.append(ProfileConfig(
                    name=profile_data["name"],
                    commandline=profile_data.get("commandline"),
                    starting_directory=profile_data.get("starting_directory"),
                    icon=profile_data.get("icon"),
                    color_scheme=profile_data.get("color_scheme"),
                    background=profile_data.get("background"),
                    font=profile_data.get("font"),
                    font_size=profile_data.get("font_size"),
                ))

        # Parse themes
        if "themes" in data:
            for theme_data in data["themes"]:
                config.themes.append(ThemeConfig(
                    name=theme_data["name"],
                    background=theme_data["background"],
                    foreground=theme_data["foreground"],
                    cursor=theme_data.get("cursor"),
                    selection=theme_data.get("selection"),
                    colors=theme_data.get("colors", {}),
                ))

        # Parse keybindings
        if "keybindings" in data:
            for kb_data in data["keybindings"]:
                config.keybindings.append(KeybindingConfig(
                    keys=kb_data["keys"],
                    action=kb_data["action"],
                    command=kb_data.get("command"),
                    args=kb_data.get("args"),
                ))

        # Parse broadcast settings
        if "broadcast" in data:
            broadcast_data = data["broadcast"]
            config.broadcast = BroadcastConfig(
                enabled=broadcast_data.get("enabled", True),
                escape_char=broadcast_data.get("escape_char", "\\"),
                timeout=broadcast_data.get("timeout", 5.0),
            )

        # Parse monitor settings
        if "monitor" in data:
            monitor_data = data["monitor"]
            config.monitor = MonitorConfig(
                follow=monitor_data.get("follow", False),
                filter=monitor_data.get("filter"),
                highlight=monitor_data.get("highlight", True),
                auto_scroll=monitor_data.get("auto_scroll", True),
            )

        return config


class ConfigLoader:
    """
    Configuration file loader.

    Handles finding, reading, and parsing configuration files
    from standard locations.
    """

    def __init__(self):
        """Initialize the config loader."""
        self._config: Optional[WT2Config] = None
        self._config_path: Optional[Path] = None

    def find_config_file(self) -> Optional[Path]:
        """
        Find the configuration file.

        Searches in standard locations:
        1. Current directory
        2. User home directory
        3. User config directory (APPDATA on Windows)

        Returns:
            Path to config file or None.
        """
        # Check current directory first
        for filename in CONFIG_FILE_NAMES:
            path = Path.cwd() / filename
            if path.exists():
                return path

        # Check home directory
        home = Path.home()
        for filename in CONFIG_FILE_NAMES:
            path = home / filename
            if path.exists():
                return path

        # Check .wt2 directory in home
        for dirname in CONFIG_DIR_NAMES:
            for filename in CONFIG_FILE_NAMES:
                path = home / dirname / filename
                if path.exists():
                    return path

        # Check APPDATA directory
        appdata = os.environ.get("APPDATA", "")
        if appdata:
            for dirname in CONFIG_DIR_NAMES:
                for filename in CONFIG_FILE_NAMES:
                    path = Path(appdata) / dirname / filename
                    if path.exists():
                        return path

        return None

    def load(
        self,
        config_path: Optional[str] = None,
        ignore_errors: bool = False,
    ) -> WT2Config:
        """
        Load configuration from file.

        Args:
            config_path: Explicit path to config file.
            ignore_errors: If True, ignore missing files and return defaults.

        Returns:
            WT2Config instance.

        Raises:
            ConfigError: If config file exists but cannot be parsed.
        """
        if config_path:
            path = Path(config_path)
            if not path.exists():
                if ignore_errors:
                    return WT2Config()
                raise ConfigError(
                    config_path=str(path),
                    reason="File not found",
                )
        else:
            path = self.find_config_file()
            if path is None:
                return WT2Config()

        self._config_path = path

        try:
            with open(path, "r", encoding="utf-8") as f:
                data = yaml.safe_load(f) or {}

        except yaml.YAMLError as e:
            raise ConfigError(
                config_path=str(path),
                reason=f"YAML parsing error: {e}",
            )

        except IOError as e:
            raise ConfigError(
                config_path=str(path),
                reason=f"IO error: {e}",
            )

        self._config = WT2Config.from_dict(data)
        return self._config

    def get(self) -> WT2Config:
        """
        Get the loaded configuration.

        Returns:
            WT2Config instance.

        Raises:
            RuntimeError: If no configuration has been loaded.
        """
        if self._config is None:
            self.load()
        return self._config

    def get_path(self) -> Optional[Path]:
        """Get the path to the loaded config file."""
        return self._config_path

    def reload(self) -> WT2Config:
        """Reload the configuration from file."""
        self._config = None
        return self.load()

    def save(
        self,
        config: WT2Config,
        config_path: Optional[str] = None,
    ) -> Path:
        """
        Save configuration to file.

        Args:
            config: Configuration to save.
            config_path: Output path (defaults to found config path).

        Returns:
            Path to saved file.
        """
        path = Path(config_path) if config_path else self._config_path
        if path is None:
            # Create default path in home directory
            path = Path.home() / ".wt2" / "wt2rc.yaml"
            path.parent.mkdir(parents=True, exist_ok=True)

        # Convert to dictionary for YAML serialization
        data = config_to_dict(config)

        with open(path, "w", encoding="utf-8") as f:
            yaml.dump(data, f, default_flow_style=False, sort_keys=False)

        self._config_path = path
        self._config = config

        return path


def config_to_dict(config: WT2Config) -> Dict[str, Any]:
    """
    Convert configuration to a dictionary.

    Args:
        config: Configuration to convert.

    Returns:
        Dictionary representation.
    """
    result = {
        "version": config.version,
    }

    # General settings
    result["general"] = {
        "default_shell": config.general.default_shell,
        "default_profile": config.general.default_profile,
        "confirmation_prompt": config.general.confirmation_prompt,
        "verbose_output": config.general.verbose_output,
        "max_history": config.general.max_history,
    }

    # Profiles
    if config.profiles:
        result["profiles"] = [
            {
                "name": p.name,
                "commandline": p.commandline,
                "starting_directory": p.starting_directory,
                "icon": p.icon,
                "color_scheme": p.color_scheme,
                "background": p.background,
                "font": p.font,
                "font_size": p.font_size,
            }
            for p in config.profiles
        ]

    # Themes
    if config.themes:
        result["themes"] = [
            {
                "name": t.name,
                "background": t.background,
                "foreground": t.foreground,
                "cursor": t.cursor,
                "selection": t.selection,
                "colors": t.colors,
            }
            for t in config.themes
        ]

    # Keybindings
    if config.keybindings:
        result["keybindings"] = [
            {
                "keys": k.keys,
                "action": k.action,
                "command": k.command,
                "args": k.args,
            }
            for k in config.keybindings
        ]

    # Broadcast settings
    result["broadcast"] = {
        "enabled": config.broadcast.enabled,
        "escape_char": config.broadcast.escape_char,
        "timeout": config.broadcast.timeout,
    }

    # Monitor settings
    result["monitor"] = {
        "follow": config.monitor.follow,
        "filter": config.monitor.filter,
        "highlight": config.monitor.highlight,
        "auto_scroll": config.monitor.auto_scroll,
    }

    return result


def parse_config(
    config_path: Optional[str] = None,
    ignore_errors: bool = True,
) -> WT2Config:
    """
    Parse configuration file.

    A convenience function for quick config loading.

    Args:
        config_path: Explicit path to config file.
        ignore_errors: If True, return default config on error.

    Returns:
        WT2Config instance.
    """
    loader = ConfigLoader()
    try:
        return loader.load(config_path)
    except ConfigError:
        if ignore_errors:
            return WT2Config()
        raise
