"""
Compatibility Validation Utilities for winterm2.

Provides validation functions to ensure the environment meets
winterm2's requirements for Windows-specific operations.
"""

import os
import sys
from typing import Tuple, Optional

from .platform import (
    is_supported_windows,
    get_windows_version,
    get_windows_version_string,
    get_shell_type,
    is_wsl,
)
from .terminal_check import is_windows_terminal_installed, is_experimental_api_enabled
from .elevation import is_admin, get_elevation_status


# Minimum requirements for winterm2
_MIN_PYTHON_VERSION = (3, 8)


class CompatibilityError(Exception):
    """Raised when environment does not meet compatibility requirements."""

    def __init__(self, message: str, suggestion: Optional[str] = None):
        super().__init__(message)
        self.suggestion = suggestion


def validate_python_version() -> Tuple[bool, str]:
    """
    Validate that the Python version meets minimum requirements.

    Returns:
        Tuple of (is_valid, error_message).
    """
    current = sys.version_info[:2]
    minimum = _MIN_PYTHON_VERSION

    if current >= minimum:
        return True, ""

    return (
        False,
        f"Python {minimum[0]}.{minimum[1]}+ is required. "
        f"Current version is {current[0]}.{current[1]}."
    )


def validate_windows_version() -> Tuple[bool, str]:
    """
    Validate that the Windows version is supported.

    Returns:
        Tuple of (is_valid, error_message).
    """
    if not is_supported_windows():
        major, minor = get_windows_version()
        return (
            False,
            f"Windows 10 21H2+ or Windows 11 is required. "
            f"Current version is {get_windows_version_string()}."
        )
    return True, ""


def validate_terminal() -> Tuple[bool, str]:
    """
    Validate that Windows Terminal is installed and configured.

    Returns:
        Tuple of (is_valid, error_message).
    """
    if not is_windows_terminal_installed():
        return (
            False,
            "Windows Terminal is not installed. "
            "Please install it from the Microsoft Store."
        )

    if not is_experimental_api_enabled():
        return (
            False,
            "Windows Terminal JSON Command API is not enabled. "
            "Please enable it in Settings > Developers."
        )

    return True, ""


def validate_environment() -> Tuple[bool, str]:
    """
    Validate the entire winterm2 environment.

    Performs comprehensive validation including:
    - Python version
    - Windows version
    - Windows Terminal installation
    - API availability

    Returns:
        Tuple of (is_valid, error_message).
        If invalid, error_message contains the first blocking issue.
    """
    # Check Python version
    valid, message = validate_python_version()
    if not valid:
        return False, message

    # Check Windows version
    valid, message = validate_windows_version()
    if not valid:
        return False, message

    # Check terminal
    valid, message = validate_terminal()
    if not valid:
        return False, message

    return True, ""


def get_shell_commands(shell_type: Optional[str] = None) -> dict:
    """
    Get shell-specific command mappings.

    Provides the correct command syntax for common operations
    based on the detected or specified shell type.

    Args:
        shell_type: Override shell type detection. If None, auto-detects.

    Returns:
        Dictionary with command mappings:
        - clear: Command to clear the screen
        - list_dir: Command to list directory contents
        - change_dir: Command to change directory
        - env_var: Prefix for environment variables
        - shell_path: Path to shell executable
    """
    if shell_type is None:
        shell_type = get_shell_type()

    # Common shell command definitions
    commands = {
        'powershell': {
            'clear': 'Clear-Host',
            'list_dir': 'Get-ChildItem',
            'change_dir': 'Set-Location',
            'env_var': '$env:',
            'shell_path': 'powershell.exe',
            'name': 'Windows PowerShell',
        },
        'powershell_core': {
            'clear': 'Clear-Host',
            'list_dir': 'Get-ChildItem',
            'change_dir': 'Set-Location',
            'env_var': '$env:',
            'shell_path': 'pwsh',
            'name': 'PowerShell Core',
        },
        'cmd': {
            'clear': 'cls',
            'list_dir': 'dir',
            'change_dir': 'cd',
            'env_var': '%',
            'shell_path': 'cmd.exe',
            'name': 'Command Prompt',
        },
        'wsl': {
            'clear': 'clear',
            'list_dir': 'ls',
            'change_dir': 'cd',
            'env_var': '$',
            'shell_path': 'wsl.exe',
            'name': 'WSL Bash',
        },
    }

    return commands.get(shell_type, commands['cmd'])


def check_feature_support(feature: str) -> Tuple[bool, str]:
    """
    Check if a specific feature is supported in the current environment.

    Args:
        feature: Name of the feature to check.
                Supported features: 'json_api', 'wsl', 'admin_ops'

    Returns:
        Tuple of (is_supported, message).
    """
    feature = feature.lower()

    if feature == 'json_api':
        if not is_windows_terminal_installed():
            return False, "Windows Terminal is not installed"
        if not is_experimental_api_enabled():
            return False, "Windows Terminal JSON API is not enabled"
        return True, "JSON API is available"

    elif feature == 'wsl':
        if not is_wsl():
            return False, "Not running inside WSL"
        return True, "WSL is available"

    elif feature == 'admin_ops':
        if not is_admin():
            return False, "Not running with administrator privileges"
        return True, "Admin operations are available"

    elif feature == 'ansi_escape':
        # Check for ANSI escape sequence support
        if sys.platform == 'win32':
            # On Windows, check if ANSI is enabled
            # Windows Terminal always supports ANSI
            term = os.environ.get('TERM_PROGRAM', '')
            if 'WindowsTerminal' in term:
                return True, "ANSI escape sequences supported (Windows Terminal)"
            # ConHost has limited support
            return True, "ANSI escape sequences supported (limited)"
        return True, "ANSI escape sequences supported"

    return False, f"Unknown feature: {feature}"


def get_compatibility_report() -> dict:
    """
    Generate a comprehensive compatibility report.

    Returns:
        Dictionary containing:
        - overall_status: 'compatible', 'warning', or 'incompatible'
        - python: Version and validation result
        - windows: Version and validation result
        - terminal: Terminal info and validation result
        - elevation: Admin status
        - features: Support status for key features
        - recommendations: List of suggested actions
    """
    python_valid, python_msg = validate_python_version()
    windows_valid, windows_msg = validate_windows_version()
    terminal_valid, terminal_msg = validate_terminal()

    # Determine overall status
    if python_valid and windows_valid and terminal_valid:
        status = 'compatible'
    elif python_valid and windows_valid:
        status = 'warning'  # Terminal issues but core can run
    else:
        status = 'incompatible'

    # Get elevation status
    elevation = get_elevation_status()

    # Check individual features
    features = {
        'json_api': check_feature_support('json_api'),
        'wsl': check_feature_support('wsl'),
        'admin_ops': check_feature_support('admin_ops'),
    }

    # Generate recommendations
    recommendations = []
    if not python_valid:
        recommendations.append(f"Python upgrade required: {python_msg}")
    if not windows_valid:
        recommendations.append(f"Windows version issue: {windows_msg}")
    if not terminal_valid:
        recommendations.append(f"Terminal setup needed: {terminal_msg}")
    if not elevation['is_admin']:
        recommendations.append("Consider running as administrator for full functionality")

    return {
        'overall_status': status,
        'python': {
            'version': f"{sys.version_info.major}.{sys.version_info.minor}.{sys.version_info.micro}",
            'valid': python_valid,
            'message': python_msg,
        },
        'windows': {
            'version': get_windows_version_string(),
            'valid': windows_valid,
            'message': windows_msg,
        },
        'terminal': {
            'installed': is_windows_terminal_installed(),
            'api_enabled': is_experimental_api_enabled(),
            'valid': terminal_valid,
            'message': terminal_msg,
        },
        'elevation': elevation,
        'features': features,
        'recommendations': recommendations,
    }


def raise_if_incompatible() -> None:
    """
    Raise a CompatibilityError if the environment is incompatible.

    Useful for early validation in CLI entry points.
    """
    valid, message = validate_environment()
    if not valid:
        raise CompatibilityError(message)
