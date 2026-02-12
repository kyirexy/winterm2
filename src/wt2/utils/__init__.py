"""Utilities package."""

from .config import (
    ConfigLoader,
    parse_config,
    WT2Config,
    ProfileConfig,
    ThemeConfig,
    KeybindingConfig,
)
from .path import (
    windows_to_wsl,
    wsl_to_windows,
    convert_path,
    is_windows_path,
    is_wsl_path,
    detect_wsl_distro,
    get_wsl_home_distro,
    normalize_path,
)
from .platform import (
    WindowsVersion,
    get_windows_version,
    get_windows_version_string,
    is_windows_10,
    is_windows_11,
    is_supported_windows,
    get_shell_type,
    get_powershell_version,
    is_wsl,
    is_powershell,
    is_cmd,
    get_terminal_type,
    get_platform_info,
)
from .terminal_check import (
    is_windows_terminal_installed,
    is_experimental_api_enabled,
    prompt_enable_api,
)
from .elevation import (
    is_admin,
    require_admin,
)
from .compat import (
    validate_environment,
    get_shell_commands,
)

__all__ = [
    # Config
    "ConfigLoader",
    "parse_config",
    "WT2Config",
    "ProfileConfig",
    "ThemeConfig",
    "KeybindingConfig",
    # Path
    "windows_to_wsl",
    "wsl_to_windows",
    "convert_path",
    "is_windows_path",
    "is_wsl_path",
    "detect_wsl_distro",
    "get_wsl_home_distro",
    "normalize_path",
    # Platform
    "WindowsVersion",
    "get_windows_version",
    "get_windows_version_string",
    "is_windows_10",
    "is_windows_11",
    "is_supported_windows",
    "get_shell_type",
    "get_powershell_version",
    "is_wsl",
    "is_powershell",
    "is_cmd",
    "get_terminal_type",
    "get_platform_info",
    # Terminal Check
    "is_windows_terminal_installed",
    "is_experimental_api_enabled",
    "prompt_enable_api",
    # Elevation
    "is_admin",
    "require_admin",
    # Compatibility
    "validate_environment",
    "get_shell_commands",
]
