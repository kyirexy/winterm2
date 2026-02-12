"""
Windows and WSL Path Conversion Utilities.

Provides robust bidirectional conversion between Windows paths and WSL paths,
handling drive letters, UNC paths, and various edge cases.
"""

import os
import re
from typing import Optional


# Regex patterns for path matching
_DRIVE_LETTER_PATTERN = re.compile(r'^([A-Za-z]):\\(.+)$')
_UNC_WSL_PATTERN = re.compile(r'^\\\\wsl\$\\([^\\]+)\\(.+)$')
_MNT_PATTERN = re.compile(r'^/mnt/([A-Za-z])/(.+)$')
_WSL_PATH_PATTERN = re.compile(r'^/([^/]+)/(.+)$')


def windows_to_wsl(path: Optional[str]) -> str:
    """
    Convert a Windows path to its WSL equivalent.

    Handles the following cases:
    - Local drive paths: D:\\foo\\bar → /mnt/d/foo/bar
    - UNC WSL paths: \\\\wsl$\\Ubuntu\\home → /mnt/c/home (simplified)

    Args:
        path: Windows path to convert. If None or empty, returns as-is.

    Returns:
        The WSL path equivalent. Returns original path if conversion
        is not possible (e.g., UNC server paths not in WSL).

    Examples:
        >>> windows_to_wsl("D:\\\\Projects\\\\file.txt")
        '/mnt/d/Projects/file.txt'
        >>> windows_to_wsl("C:\\\\Users\\\\Admin")
        '/mnt/c/Users/Admin'
    """
    if not path:
        return path

    # Match standard drive letter paths (e.g., D:\\foo\\bar)
    match = _DRIVE_LETTER_PATTERN.match(path)
    if match:
        drive = match.group(1).lower()
        # Convert backslashes to forward slashes
        rest = match.group(2).replace('\\', '/')
        return f"/mnt/{drive}/{rest}"

    # Match WSL UNC paths (e.g., \\\\wsl$\\Ubuntu\\home\\user)
    # These are Windows paths that point to WSL filesystems
    unc_match = _UNC_WSL_PATTERN.match(path)
    if unc_match:
        # distro = unc_match.group(1)  # Could be used for more specific handling
        rest = unc_match.group(2).replace('\\', '/')
        # Default to /mnt/c for the converted path
        return f"/mnt/c/{rest}"

    # Return as-is if no pattern matched
    return path


def wsl_to_windows(path: Optional[str]) -> str:
    """
    Convert a WSL path to its Windows equivalent.

    Handles the following cases:
    - Mounted drives: /mnt/d/foo/bar → D:/foo/bar
    - WSL distribution paths: /home/user/file → \\\\wsl$\\Distro\\home\\user\\file

    Args:
        path: WSL path to convert. If None or empty, returns as-is.

    Returns:
        The Windows path equivalent. Returns original path if conversion
        is not possible.

    Examples:
        >>> wsl_to_windows("/mnt/d/Projects/file.txt")
        'D:/Projects/file.txt'
        >>> wsl_to_windows("/home/user/docs")
        '\\\\wsl$\\Distro/home/user/docs'
    """
    if not path:
        return path

    # Match /mnt/x/ pattern for mounted Windows drives
    mnt_match = _MNT_PATTERN.match(path)
    if mnt_match:
        drive = mnt_match.group(1).upper()
        rest = mnt_match.group(2).replace('/', '\\')
        return f"{drive}:\\{rest}"

    # Match general WSL paths (not /mnt/*)
    wsl_match = _WSL_PATH_PATTERN.match(path)
    if wsl_match:
        distro = wsl_match.group(1)
        rest = wsl_match.group(2).replace('/', '\\')
        return f"\\\\wsl$\\{distro}\\{rest}"

    return path


def detect_wsl_distro() -> str:
    """
    Detect the default WSL distribution.

    Uses wsl.exe --list --quiet to get the default distribution name.

    Returns:
        Name of the default WSL distribution, or empty string if
        WSL is not available or no distributions are installed.

    Note:
        This only works on Windows with WSL installed.
        On non-Windows systems or when wsl.exe is not available,
        returns an empty string.
    """
    try:
        import subprocess
        result = subprocess.run(
            ["wsl.exe", "--list", "--quiet"],
            capture_output=True,
            text=True,
            timeout=5
        )
        if result.returncode == 0 and result.stdout:
            distros = result.stdout.strip().split('\n')
            # Filter out empty strings
            distros = [d for d in distros if d]
            return distros[0] if distros else ""
    except (FileNotFoundError, subprocess.TimeoutExpired, Exception):
        pass

    return ""


def get_wsl_home_distro() -> str:
    """
    Get the Windows path to the current user's home directory in WSL.

    Returns:
        Windows UNC path to the WSL home directory, e.g.:
        \\\\wsl$\\Ubuntu\\home\\username
    """
    distro = detect_wsl_distro()
    if not distro:
        return ""

    # Try to get the home directory
    try:
        import subprocess
        result = subprocess.run(
            ["wsl.exe", "-e", "bash", "-c", "echo $HOME"],
            capture_output=True,
            text=True,
            timeout=5
        )
        if result.returncode == 0:
            wsl_home = result.stdout.strip()
            return wsl_to_windows(wsl_home)
    except Exception:
        pass

    # Fallback to default path
    return f"\\\\wsl$\\{distro}\\home"


def is_windows_path(path: str) -> bool:
    """
    Check if a path appears to be a Windows path.

    Args:
        path: Path to check.

    Returns:
        True if path appears to be a Windows path (has drive letter
        or UNC format), False otherwise.
    """
    if not path:
        return False

    return bool(_DRIVE_LETTER_PATTERN.match(path) or path.startswith('\\\\'))


def is_wsl_path(path: str) -> bool:
    """
    Check if a path appears to be a WSL path.

    Args:
        path: Path to check.

    Returns:
        True if path appears to be a WSL path (starts with /), False otherwise.
    """
    if not path:
        return False

    return path.startswith('/') and not is_windows_path(path)


def normalize_path(path: str, prefer_wsl: bool = True) -> str:
    """
    Normalize a path to use consistent separators.

    Args:
        path: Path to normalize.
        prefer_wsl: If True, convert to WSL format. If False, use Windows format.

    Returns:
        Normalized path with consistent separators.
    """
    if not path:
        return path

    if prefer_wsl:
        # Convert to WSL format
        if is_windows_path(path):
            return windows_to_wsl(path)
        # Normalize separators
        return path.replace('\\', '/')
    else:
        # Convert to Windows format
        if is_wsl_path(path):
            return wsl_to_windows(path)
        # Normalize separators
        return path.replace('/', '\\')


def convert_path(path: str, to_wsl: bool) -> str:
    """
    Convert a path between Windows and WSL formats.

    Args:
        path: Path to convert.
        to_wsl: If True, convert to WSL format. If False, convert to Windows format.

    Returns:
        Converted path.
    """
    if not path:
        return path

    if to_wsl:
        return windows_to_wsl(path)
    else:
        return wsl_to_windows(path)
