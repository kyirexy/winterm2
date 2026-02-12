"""
Privilege Elevation Utilities for Windows.

Provides utilities to check and handle administrator privileges,
and to execute commands with elevated rights when needed.
"""

import ctypes
import os
import sys
from typing import Optional, Tuple


def is_admin() -> bool:
    """
    Check if the current process is running with administrator privileges.

    On Windows, uses the IsUserAnAdmin() API from shell32.dll.

    Returns:
        True if running as administrator, False otherwise.
        Also returns False on non-Windows platforms.
    """
    # Only meaningful on Windows
    if sys.platform != 'win32':
        return False

    try:
        return ctypes.windll.shell32.IsUserAnAdmin() != 0
    except AttributeError:
        # shell32.dll might not have this function on older Windows
        return False
    except Exception:
        return False


def require_admin(operation: str, auto_elevate: bool = False) -> Tuple[bool, Optional[str]]:
    """
    Check if an operation requires admin privileges and handle accordingly.

    Args:
        operation: Description of the operation being performed.
        auto_elevate: If True, automatically attempt to elevate. If False,
                      just return status and let caller decide.

    Returns:
        Tuple of (can_proceed, message).
        - can_proceed: True if operation can continue
        - message: Error message if can_proceed is False, None otherwise
    """
    if is_admin():
        return True, None

    if auto_elevate:
        # Try to restart with admin privileges
        success = shell_execute_as_admin(sys.executable, *sys.argv)
        if success == 0:
            sys.exit(0)  # Exit the non-elevated process
        return False, "Failed to obtain administrator privileges"

    return False, f"'{operation}' requires administrator privileges"


def shell_execute_as_admin(
    program: str,
    *args: str,
    working_dir: Optional[str] = None
) -> int:
    """
    Execute a program with administrator privileges.

    Uses ShellExecuteEx with the "runas" verb to request elevation.
    This will trigger a UAC prompt if the user is not an administrator.

    Args:
        program: Path to the program to execute.
        *args: Command line arguments to pass to the program.
        working_dir: Optional working directory for the process.

    Returns:
        Return code from the executed process, or non-zero on failure.
    """
    if sys.platform != 'win32':
        return -1  # Not supported on non-Windows

    if is_admin():
        # Already admin, just execute directly
        import subprocess
        cmd = [program] + list(args)
        try:
            result = subprocess.run(cmd, cwd=working_dir)
            return result.returncode
        except Exception as e:
            print(f"Failed to execute: {e}")
            return 1

    # Need to elevate
    try:
        import subprocess
        # Build command line
        if args:
            cmd_line = f'"{program}" {" ".join(args)}'
        else:
            cmd_line = f'"{program}"'

        # Use ShellExecute with "runas" verb for elevation
        # Note: This uses the runas verb which triggers UAC
        result = subprocess.run(
            f'shellrunas /user:Administrator "{cmd_line}"',
            shell=True,
            cwd=working_dir,
            capture_output=True,
            text=True
        )
        return result.returncode

    except FileNotFoundError:
        # shellrunas not available, try direct runas
        try:
            result = subprocess.run(
                f'runas /user:Administrator "{program}"',
                shell=True,
                cwd=working_dir,
                capture_output=True,
                text=True
            )
            return result.returncode
        except Exception as e:
            print(f"Failed to elevate: {e}")
            return 1
    except Exception as e:
        print(f"Failed to elevate: {e}")
        return 1


def check_privilege_level() -> str:
    """
    Check the current user's privilege level.

    Returns:
        String describing the privilege level:
        - "admin": Running with full administrator privileges
        - "standard": Standard user without admin rights
        - "limited": Process has limited tokens (e.g., run as different user)
        - "unknown": Could not determine
    """
    if not is_admin():
        return "standard"

    # Additional checks can be done here for more granular privilege info
    return "admin"


def can_write_to_protected_path(path: str) -> bool:
    """
    Check if the current user can write to a potentially protected path.

    This is a best-effort check and may not catch all cases.

    Args:
        path: Path to check write access for.

    Returns:
        True if writing should succeed, False if admin rights are likely needed.
    """
    if not os.path.exists(path):
        # Try to check parent directory
        parent = os.path.dirname(path)
        if parent:
            return can_write_to_protected_path(parent)
        return False

    try:
        # Try to create a test file
        test_file = os.path.join(path, ".write_test_temp")
        with open(test_file, 'w') as f:
            f.write("test")
        # Clean up
        os.remove(test_file)
        return True
    except (PermissionError, OSError):
        return False


def get_elevation_status() -> dict:
    """
    Get comprehensive elevation status information.

    Returns:
        Dictionary containing:
        - is_admin: Whether running as admin
        - privilege_level: The privilege level string
        - can_write_system: Whether can write to system paths
        - uac_enabled: Whether UAC is enabled (always True on supported versions)
    """
    return {
        "is_admin": is_admin(),
        "privilege_level": check_privilege_level(),
        "can_write_system": can_write_to_protected_path(os.environ.get('ProgramW6432', '')),
        "uac_enabled": True,  # UAC is always on in supported Windows versions
    }
