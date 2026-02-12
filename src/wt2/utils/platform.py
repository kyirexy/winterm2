"""
Platform Detection Utilities for Windows.

Provides comprehensive detection of Windows version, shell type,
and other platform-specific information needed by winterm2.
"""

import os
import sys
import platform
from enum import Enum
from typing import Optional, Tuple


class WindowsVersion(Enum):
    """Enumeration of supported Windows versions."""
    WIN10_21H2 = "21H2"  # Build 19044, released November 2021
    WIN10_22H2 = "22H2"  # Build 19045, released October 2022
    WIN11_21H2 = "21H2"  # Build 22000, released October 2021
    WIN11_22H2 = "22H2"  # Build 22621, released September 2022
    WIN11_23H2 = "23H2"  # Build 22631, released late 2023
    UNKNOWN = "Unknown"


# Minimum supported builds for each feature
_MIN_WIN10_BUILD_FOR_SUPPORT = 19044  # 21H2
_MIN_WIN11_BUILD = 22000


def get_windows_version() -> Tuple[int, int, int]:
    """
    Get the full Windows version information.

    Returns:
        Tuple of (major, minor, build) version numbers.
        For example, Windows 11 22H2 returns (10, 0, 22621).

    Note:
        On non-Windows platforms, returns (0, 0, 0).
    """
    if sys.platform != 'win32':
        return (0, 0, 0)

    try:
        ver = sys.getwindowsversion()
        return (ver.major, ver.minor, ver.build)
    except Exception:
        # Fallback using platform module
        try:
            ver = platform.version()
            parts = ver.split('.')
            major = int(parts[0]) if len(parts) > 0 else 0
            minor = int(parts[1]) if len(parts) > 1 else 0
            build = int(parts[2]) if len(parts) > 2 else 0
            return (major, minor, build)
        except Exception:
            return (0, 0, 0)


def get_windows_version_string() -> str:
    """
    Get a human-readable Windows version string.

    Returns:
        Version string like "Windows 10 21H2" or "Windows 11 22H2".
        Returns "Unknown" or "Not Windows" for non-Windows platforms.
    """
    if sys.platform != 'win32':
        return "Not Windows"

    major, minor, build = get_windows_version()

    if major == 10:
        # Determine if it's Windows 10 or 11 based on build
        if build >= _MIN_WIN11_BUILD:
            # Windows 11 starts at build 22000
            # Map build numbers to releases
            if build >= 22631:
                return "Windows 11 23H2"
            elif build >= 22621:
                return "Windows 11 22H2"
            else:
                return "Windows 11"
        else:
            # Windows 10
            if build >= 19045:
                return "Windows 10 22H2"
            elif build >= 19044:
                return "Windows 10 21H2"
            else:
                return "Windows 10"
    elif major > 10:
        return f"Windows (version {major}.{minor}, build {build})"
    else:
        return f"Windows {major}.{minor}"


def is_windows_10() -> bool:
    """Check if running Windows 10 (not Windows 11)."""
    major, minor, build = get_windows_version()
    return major == 10 and build < _MIN_WIN11_BUILD


def is_windows_11() -> bool:
    """Check if running Windows 11."""
    major, minor, build = get_windows_version()
    return major == 10 and build >= _MIN_WIN11_BUILD


def is_supported_windows() -> bool:
    """
    Check if the Windows version is supported by winterm2.

    Supported versions:
    - Windows 10 21H2 (build 19044) and later
    - Windows 11 all versions

    Returns:
        True if supported, False otherwise.
    """
    if sys.platform != 'win32':
        return False

    major, minor, build = get_windows_version()

    if major < 10:
        return False

    if major > 10:
        # Windows 12+ (future proofing)
        return True

    # Windows 10
    return build >= _MIN_WIN10_BUILD_FOR_SUPPORT


def get_shell_type() -> str:
    """
    Detect the current shell type.

    Checks multiple indicators to determine the running shell:
    - WSL environment variable
    - PowerShell indicators in environment or executable name
    - CMD executable name

    Returns:
        One of: 'wsl', 'powershell', 'powershell_core', 'cmd', 'unknown'
    """
    # Check if running in WSL
    if os.environ.get('WSL_DISTRO_NAME'):
        return 'wsl'

    # Check PowerShell indicators
    pwsh_channel = os.environ.get('POWERSHELL_DISTRIBUTION_CHANNEL', '')
    if 'PowerShell' in pwsh_channel:
        return 'powershell'

    # Check executable name
    exe_name = os.path.basename(sys.executable).lower()
    if 'pwsh' in exe_name:
        return 'powershell_core'
    if 'powershell' in exe_name:
        return 'powershell'

    # Check for CMD (command.com is not used in modern Windows)
    if 'cmd' in exe_name:
        return 'cmd'

    # Default to unknown
    return 'unknown'


def get_powershell_version() -> Tuple[int, int]:
    """
    Get the PowerShell version if running in PowerShell.

    Only works for PowerShell Core (pwsh), not Windows PowerShell (powershell.exe).

    Returns:
        Tuple of (major, minor) version numbers, e.g., (7, 4).
        Returns (0, 0) if not running in PowerShell.
    """
    shell = get_shell_type()
    if shell not in ('powershell', 'powershell_core'):
        return (0, 0)

    try:
        import subprocess
        result = subprocess.run(
            ['pwsh', '-NoLogo', '-Command', '$PSVersionTable.PSVersion'],
            capture_output=True,
            text=True,
            timeout=10
        )
        if result.returncode == 0:
            output = result.stdout.strip()
            # Parse version string like "Major: 7, Minor: 4"
            for line in output.split('\n'):
                if line.startswith('Major'):
                    major = int(line.split(':')[1].strip())
                    # Try to get minor version
                    for l2 in output.split('\n'):
                        if l2.startswith('Minor'):
                            minor = int(l2.split(':')[1].strip())
                            return (major, minor)
                    return (major, 0)
    except Exception:
        pass

    return (0, 0)


def is_wsl() -> bool:
    """Check if running inside WSL (Windows Subsystem for Linux)."""
    return get_shell_type() == 'wsl'


def is_powershell() -> bool:
    """Check if running in PowerShell (any version)."""
    shell = get_shell_type()
    return shell in ('powershell', 'powershell_core')


def is_cmd() -> bool:
    """Check if running in Windows CMD."""
    return get_shell_type() == 'cmd'


def get_terminal_type() -> str:
    """
    Detect the terminal type being used.

    Returns:
        String describing the terminal:
        - 'windows_terminal': Windows Terminal
        - 'conhost': Windows Console (CMD default)
        - 'wt': Windows Terminal (alternative check)
        - 'unknown': Could not determine
    """
    # Check for Windows Terminal environment variable
    wt_app_id = os.environ.get('WT_APPID', '')
    if wt_app_id:
        return 'windows_terminal'

    # Check for Windows Terminal in process name or TERM
    term = os.environ.get('TERM', '')
    if 'windows' in term.lower():
        return 'windows_terminal'

    # Check if ConHost is being used (default for CMD)
    # This is harder to detect from within the process
    if os.environ.get('TERM_PROGRAM') == 'WindowsTerminal':
        return 'windows_terminal'

    # Default fallback
    return 'unknown'


def get_platform_info() -> dict:
    """
    Get comprehensive platform information.

    Returns:
        Dictionary containing all platform detection results.
    """
    major, minor, build = get_windows_version()

    return {
        "platform": sys.platform,
        "windows_version": get_windows_version_string(),
        "windows_major": major,
        "windows_minor": minor,
        "windows_build": build,
        "is_windows_10": is_windows_10(),
        "is_windows_11": is_windows_11(),
        "is_supported": is_supported_windows(),
        "is_wsl": is_wsl(),
        "is_powershell": is_powershell(),
        "is_cmd": is_cmd(),
        "shell_type": get_shell_type(),
        "terminal_type": get_terminal_type(),
        "python_executable": sys.executable,
        "python_version": sys.version,
        "wsl_distro": os.environ.get('WSL_DISTRO_NAME', ''),
    }
