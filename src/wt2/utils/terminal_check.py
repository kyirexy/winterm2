"""
Terminal API Status Detection for Windows Terminal.

Provides utilities to check if Windows Terminal is installed and if the
Experimental JSON API is enabled, which is required for winterm2 operations.
"""

import os
import json
from typing import Optional


# Default Windows Terminal installation paths
_WINDOWS_TERMINAL_PATHS = [
    os.path.expandvars(r"%LOCALAPPDATA%\Microsoft\Windows Terminal"),
    os.path.expandvars(r"%LOCALAPPDATA%\Microsoft\Windows Terminal\1.0"),
    os.path.expandvars(r"%PROGRAMFILES%\Windows Terminal"),
    r"C:\Program Files\Windows Terminal",
    r"C:\Program Files (x86)\Windows Terminal",
]

# Windows Terminal settings location in local app data
_SETTINGS_PATH_TEMPLATE = os.path.expandvars(
    r"%LOCALAPPDATA%\Packages\Microsoft.WindowsTerminal_8wekyb3td8\LocalState\settings.json"
)


def is_windows_terminal_installed() -> bool:
    """
    Check if Windows Terminal is installed on the system.

    Checks multiple common installation paths including:
    - %LOCALAPPDATA%\Microsoft\Windows Terminal (per-user install)
    - %PROGRAMFILES%\Windows Terminal (system-wide install)

    Returns:
        True if Windows Terminal executable is found, False otherwise.
    """
    for path in _WINDOWS_TERMINAL_PATHS:
        # Check for the main executable
        exe_path = os.path.join(path, "wt.exe")
        if os.path.exists(exe_path):
            return True

        # Also check for WindowsTerminal.exe (older versions)
        alt_exe_path = os.path.join(path, "WindowsTerminal.exe")
        if os.path.exists(alt_exe_path):
            return True

    return False


def is_experimental_api_enabled(settings_path: Optional[str] = None) -> bool:
    """
    Check if the Experimental JSON Command API is enabled in Windows Terminal.

    The Experimental JSON API is required for winterm2 to communicate with
    Windows Terminal via JSON commands.

    Args:
        settings_path: Optional path to settings.json. If not provided,
                       uses the default Windows Terminal settings location.

    Returns:
        True if the experimental API is enabled, False otherwise.
    """
    if settings_path is None:
        settings_path = _SETTINGS_PATH_TEMPLATE

    if not os.path.exists(settings_path):
        return False

    try:
        with open(settings_path, 'r', encoding='utf-8') as f:
            settings = json.load(f)

        # Check for experimental API setting
        # The setting can be at different locations depending on version
        experimental = settings.get("experimental", {})
        if isinstance(experimental, bool):
            # Some versions use boolean directly
            return experimental

        # Newer versions use nested object
        return experimental.get("enableJsonApi", False)

    except (json.JSONDecodeError, PermissionError, OSError):
        return False


def prompt_enable_api() -> None:
    """
    Display a user-friendly prompt explaining how to enable the JSON API.

    This is called when the experimental API is not enabled and winterm2
    cannot function without it. The prompt guides users through the
    settings UI or direct JSON editing.
    """
    message = """
Windows Terminal JSON Command API is not enabled.

To use winterm2, please enable it:

Option 1 - Via Settings UI:
1. Open Windows Terminal
2. Press Ctrl+, (comma) to open Settings
3. Go to the "Developers" section
4. Toggle on "Experimental JSON Command API"
5. Restart Windows Terminal

Option 2 - Via JSON Settings:
Edit your settings.json file and add:
{
    "experimental": {
        "enableJsonApi": true
    }
}

Location of settings.json:
%LOCALAPPDATA%\\Packages\\Microsoft.WindowsTerminal_8wekyb3td8\\LocalState\\settings.json
"""
    print(message)


def get_terminal_info() -> dict:
    """
    Get comprehensive information about the Windows Terminal installation.

    Returns:
        Dictionary containing:
        - installed: Whether Windows Terminal is installed
        - api_enabled: Whether the experimental API is enabled
        - settings_path: Path to the settings file
        - version: Terminal version (if available)
    """
    settings_path = _SETTINGS_PATH_TEMPLATE

    result = {
        "installed": is_windows_terminal_installed(),
        "api_enabled": is_experimental_api_enabled(settings_path),
        "settings_path": settings_path,
        "version": None,
    }

    # Try to get version from settings
    if os.path.exists(settings_path):
        try:
            with open(settings_path, 'r', encoding='utf-8') as f:
                settings = json.load(f)
            result["version"] = settings.get("version", None)
        except (json.JSONDecodeError, PermissionError):
            pass

    return result
