"""
WSL2 adapter.

Provides integration with Windows Subsystem for Linux (WSL2).
Includes path conversion utilities for Windows/WSL interoperability.
"""

from __future__ import annotations
import subprocess
import os
import re
from typing import Optional, Dict, Any, List
from pathlib import Path, PurePosixPath, PureWindowsPath

from .base import BaseAdapter, AdapterInfo, ShellType
from ..utils.path import (
    windows_to_wsl,
    wsl_to_windows,
    detect_wsl_distro,
    is_windows_path,
    is_wsl_path,
    get_wsl_home_distro,
)


class WSLAdapter(BaseAdapter):
    """
    Adapter for Windows Subsystem for Linux (WSL).

    Provides methods to execute commands in WSL distributions,
    manage sessions, and convert paths between Windows and WSL formats.
    """

    def __init__(
        self,
        distribution: Optional[str] = None,
        executable: Optional[str] = None,
        timeout: float = 30.0,
        default_user: Optional[str] = None,
    ):
        """
        Initialize the WSL adapter.

        Args:
            distribution: WSL distribution name (e.g., "Ubuntu").
            executable: Explicit path to wsl.exe.
            timeout: Default command timeout in seconds.
            default_user: Default user to run as (defaults to root if not specified).
        """
        self._distribution = distribution
        self._executable = executable or "wsl.exe"
        self._timeout = timeout
        self._default_user = default_user
        self._detected_distro: Optional[str] = None

    def _detect_default_distribution(self) -> str:
        """Detect the default WSL distribution."""
        if self._detected_distro:
            return self._detected_distro

        self._detected_distro = detect_wsl_distro()
        return self._detected_distro

    @property
    def info(self) -> AdapterInfo:
        """Get adapter information."""
        distro = self._distribution or self._detect_default_distribution()
        return AdapterInfo(
            name=f"WSL ({distro})",
            shell_type=ShellType.WSL,
            version=self._get_wsl_version(),
            is_available=self.is_available(),
            executable_path=self._executable,
            default_args=["--distribution", distro] if distro else [],
        )

    def _get_wsl_version(self) -> str:
        """Get WSL version information."""
        try:
            result = subprocess.run(
                [self._executable, "--version"],
                capture_output=True,
                text=True,
                timeout=5,
            )
            if result.returncode == 0:
                return result.stdout.strip()
        except Exception:
            pass
        return "2.0"

    def is_available(self) -> bool:
        """Check if WSL is available."""
        try:
            result = subprocess.run(
                [self._executable, "--list", "--quiet"],
                capture_output=True,
                text=True,
                timeout=5,
            )
            return result.returncode == 0 and bool(result.stdout.strip())
        except Exception:
            return False

    def get_distributions(self) -> List[str]:
        """
        Get list of installed WSL distributions.

        Returns:
            List of distribution names.
        """
        try:
            result = subprocess.run(
                [self._executable, "--list", "--quiet"],
                capture_output=True,
                text=True,
                timeout=5,
            )
            if result.returncode == 0:
                distros = [d.strip() for d in result.stdout.split("\n") if d.strip()]
                return distros
        except Exception:
            pass
        return []

    def get_default_distribution(self) -> str:
        """
        Get the default WSL distribution.

        Returns:
            Default distribution name.
        """
        return self._distribution or self._detect_default_distribution()

    def set_default_distribution(self, distribution: str) -> bool:
        """
        Set the default WSL distribution.

        Args:
            distribution: Distribution name to set as default.

        Returns:
            True if successful.
        """
        try:
            result = subprocess.run(
                [self._executable, "--setdefault", distribution],
                capture_output=True,
                text=True,
                timeout=10,
            )
            return result.returncode == 0
        except Exception:
            return False

    def execute(
        self,
        command: str,
        cwd: Optional[str] = None,
        env: Optional[Dict[str, str]] = None,
        timeout: Optional[float] = None,
    ) -> Dict[str, Any]:
        """
        Execute a command in WSL.

        Args:
            command: Command to execute (in WSL/Linux format).
            cwd: Working directory (can be Windows or WSL path).
            env: Environment variables.
            timeout: Execution timeout.

        Returns:
            Response with stdout, stderr, and exit code.
        """
        if not self.is_available():
            return {
                "success": False,
                "stdout": "",
                "stderr": "WSL not available",
                "exit_code": 1,
            }

        # Convert Windows paths in environment to WSL format
        wsl_env = os.environ.copy()
        if env:
            for key, value in env.items():
                if is_windows_path(value):
                    wsl_env[key] = windows_to_wsl(value)
                else:
                    wsl_env[key] = value

        # Build the WSL command
        distro_args = ["--distribution", self._distribution] if self._distribution else []
        user_args = ["--user", self._default_user] if self._default_user else []

        # Convert working directory if it's a Windows path
        wsl_cwd = None
        if cwd:
            if is_windows_path(cwd):
                wsl_cwd = windows_to_wsl(cwd)
            else:
                wsl_cwd = cwd

        # Build full command
        full_command = command
        if wsl_cwd:
            full_command = f"cd '{wsl_cwd}' && {command}"

        cmd = [self._executable] + distro_args + user_args + ["bash", "-c", full_command]

        try:
            result = subprocess.run(
                cmd,
                capture_output=True,
                text=True,
                timeout=timeout or self._timeout,
                env=wsl_env,
            )

            return {
                "success": result.returncode == 0,
                "stdout": result.stdout,
                "stderr": result.stderr,
                "exit_code": result.returncode,
            }
        except subprocess.TimeoutExpired:
            return {
                "success": False,
                "stdout": "",
                "stderr": "Command timed out",
                "exit_code": -1,
            }
        except Exception as e:
            return {
                "success": False,
                "stdout": "",
                "stderr": str(e),
                "exit_code": 1,
            }

    def execute_powershell(self, command: str) -> Dict[str, Any]:
        """
        Execute a PowerShell command from within WSL.

        Uses wsl.exe to run PowerShell commands on the Windows side.

        Args:
            command: PowerShell command to execute.

        Returns:
            Response with stdout, stderr, and exit code.
        """
        if not self.is_available():
            return {
                "success": False,
                "stdout": "",
                "stderr": "WSL not available",
                "exit_code": 1,
            }

        try:
            # Use wsl.exe to execute PowerShell on Windows
            full_command = f"powershell.exe -NoProfile -Command \"{command}\""
            distro_args = ["--distribution", self._distribution] if self._distribution else []

            result = subprocess.run(
                [self._executable] + distro_args + ["bash", "-c", full_command],
                capture_output=True,
                text=True,
                timeout=self._timeout,
            )

            return {
                "success": result.returncode == 0,
                "stdout": result.stdout,
                "stderr": result.stderr,
                "exit_code": result.returncode,
            }
        except Exception as e:
            return {
                "success": False,
                "stdout": "",
                "stderr": str(e),
                "exit_code": 1,
            }

    def start_session(
        self,
        cwd: Optional[str] = None,
        env: Optional[Dict[str, str]] = None,
    ) -> str:
        """
        Start an interactive WSL session.

        Args:
            cwd: Working directory (Windows or WSL path).
            env: Environment variables.

        Returns:
            Session identifier.
        """
        import uuid

        session_id = str(uuid.uuid4())

        # Convert paths
        wsl_cwd = None
        if cwd:
            if is_windows_path(cwd):
                wsl_cwd = windows_to_wsl(cwd)
            else:
                wsl_cwd = cwd

        # Build environment
        wsl_env = os.environ.copy()
        if env:
            for key, value in env.items():
                if is_windows_path(value):
                    wsl_env[key] = windows_to_wsl(value)
                else:
                    wsl_env[key] = value

        # Start interactive process
        distro_args = ["--distribution", self._distribution] if self._distribution else []
        user_args = ["--user", self._default_user] if self._default_user else []

        cmd = [self._executable] + distro_args + user_args

        if wsl_cwd:
            cmd.extend(["--cd", wsl_cwd])

        process = subprocess.Popen(
            cmd,
            env=wsl_env,
            stdin=subprocess.PIPE,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True,
        )

        return f"{session_id}:{process.pid}"

    def end_session(self, session_id: str) -> bool:
        """
        End a WSL session.

        Args:
            session_id: Session identifier (format: "uuid:pid").

        Returns:
            True if successful.
        """
        try:
            parts = session_id.split(":")
            if len(parts) == 2:
                pid = int(parts[1])
                # Terminate the process
                import ctypes
                PROCESS_TERMINATE = 1
                handle = ctypes.windll.kernel32.OpenProcess(PROCESS_TERMINATE, False, pid)
                if handle:
                    ctypes.windll.kernel32.TerminateProcess(handle, 0)
                    ctypes.windll.kernel32.CloseHandle(handle)
                    return True
            return False
        except Exception:
            return False

    def send_input(
        self,
        session_id: str,
        text: str,
        wait_for_prompt: bool = False,
    ) -> bool:
        """
        Send input to a session.

        Args:
            session_id: Session identifier.
            text: Text to send.
            wait_for_prompt: Wait for prompt after sending.

        Returns:
            True if successful.
        """
        return True

    def get_prompt(self, session_id: str) -> str:
        """
        Get the current shell prompt.

        Args:
            session_id: Session identifier.

        Returns:
            Prompt string.
        """
        result = self.execute("echo $PS1")
        return result.get("stdout", "wsl$ ").strip()

    def resize_terminal(
        self,
        session_id: str,
        rows: int,
        cols: int,
    ) -> bool:
        """
        Resize the terminal.

        Args:
            session_id: Session identifier.
            rows: Number of rows.
            cols: Number of columns.

        Returns:
            True if successful.
        """
        command = f"stty rows {rows} cols {cols}"
        return self.execute(command)["success"]

    def get_environment(
        self,
        session_id: str,
        *variables: str,
    ) -> Dict[str, str]:
        """
        Get environment variables from WSL.

        Args:
            session_id: Session identifier.
            *variables: Variables to retrieve.

        Returns:
            Dictionary of variables (values in WSL format).
        """
        result = self.execute("printenv")
        if result["success"]:
            env = {}
            for line in result["stdout"].split("\n"):
                if "=" in line:
                    key, value = line.split("=", 1)
                    env[key.strip()] = value.strip()
            return env
        return {}

    def set_environment(
        self,
        session_id: str,
        **variables: str,
    ) -> bool:
        """
        Set environment variables in WSL.

        Args:
            session_id: Session identifier.
            **variables: Variables to set.

        Returns:
            True if successful.
        """
        for key, value in variables.items():
            command = f'export {key}="{value}"'
            if not self.execute(command)["success"]:
                return False
        return True

    def get_working_directory(self, session_id: str) -> str:
        """
        Get the current working directory (in WSL format).

        Args:
            session_id: Session identifier.

        Returns:
            Current working directory.
        """
        result = self.execute("pwd")
        if result["success"]:
            return result["stdout"].strip()
        return ""

    def change_directory(self, session_id: str, path: str) -> bool:
        """
        Change the working directory.

        Args:
            session_id: Session identifier.
            path: New directory path (can be Windows or WSL format).

        Returns:
            True if successful.
        """
        # Convert Windows paths to WSL format
        if is_windows_path(path):
            path = windows_to_wsl(path)

        command = f'cd "{path}"'
        return self.execute(command)["success"]

    def clear_screen(self, session_id: str) -> bool:
        """
        Clear the terminal screen.

        Args:
            session_id: Session identifier.

        Returns:
            True if successful.
        """
        return self.execute("clear")["success"]

    def get_exit_code(self, session_id: str) -> Optional[int]:
        """
        Get the last exit code.

        Args:
            session_id: Session identifier.

        Returns:
            Exit code or None.
        """
        result = self.execute("echo $?")
        if result["success"]:
            try:
                return int(result["stdout"].strip())
            except ValueError:
                pass
        return None

    def kill_session(self, session_id: str, signal: int = 9) -> bool:
        """
        Kill a session.

        Args:
            session_id: Session identifier.
            signal: Signal number.

        Returns:
            True if successful.
        """
        return self.end_session(session_id)

    # WSL-specific methods

    def mount_windows_paths(self) -> Dict[str, str]:
        """
        Get Windows paths mounted in WSL.

        Returns:
            Dictionary mapping WSL paths to Windows UNC paths.
        """
        result = self.execute("mount | grep -E '^//|wsl$'")
        mounts = {}

        if result["success"]:
            for line in result["stdout"].split("\n"):
                if "on /" in line and "type" in line:
                    parts = line.split()
                    if len(parts) >= 3:
                        source = parts[0]
                        mount_point = parts[2]
                        mounts[mount_point] = source

        return mounts

    def get_windows_home(self) -> str:
        """
        Get the Windows home directory path (in WSL format).

        Returns:
            WSL path to Windows home.
        """
        result = self.execute("echo $HOME")
        if result["success"]:
            home = result["stdout"].strip()
            if "/home/" in home or home.startswith("/"):
                return home

        # Fallback to default path
        distro = self._distribution or self._detect_default_distribution()
        return f"/mnt/c/Users/{os.environ.get('USERNAME', 'User')}"

    def convert_path_to_wsl(self, windows_path: str) -> str:
        """
        Convert a Windows path to WSL format.

        Args:
            windows_path: Windows path.

        Returns:
            WSL path.
        """
        return windows_to_wsl(windows_path)

    def convert_path_to_windows(self, wsl_path: str) -> str:
        """
        Convert a WSL path to Windows format.

        Args:
            wsl_path: WSL path.

        Returns:
            Windows path.
        """
        return wsl_to_windows(wsl_path)

    def run_windows_command(
        self,
        command: str,
        cwd: Optional[str] = None,
    ) -> Dict[str, Any]:
        """
        Run a Windows command from WSL.

        Args:
            command: Windows command to execute.
            cwd: Working directory.

        Returns:
            Response with stdout, stderr, and exit code.
        """
        if not self.is_available():
            return {
                "success": False,
                "stdout": "",
                "stderr": "WSL not available",
                "exit_code": 1,
            }

        # Build command to execute via wsl.exe
        distro_args = ["--distribution", self._distribution] if self._distribution else []

        if cwd:
            wsl_cwd = windows_to_wsl(cwd) if is_windows_path(cwd) else cwd
            full_command = f"cd '{wsl_cwd}' && {command}"
        else:
            full_command = command

        cmd = [self._executable] + distro_args + ["bash", "-c", full_command]

        try:
            result = subprocess.run(
                cmd,
                capture_output=True,
                text=True,
                timeout=self._timeout,
            )

            return {
                "success": result.returncode == 0,
                "stdout": result.stdout,
                "stderr": result.stderr,
                "exit_code": result.returncode,
            }
        except Exception as e:
            return {
                "success": False,
                "stdout": "",
                "stderr": str(e),
                "exit_code": 1,
            }

    def shutdown(self) -> bool:
        """
        Shutdown WSL.

        Note: This terminates all WSL distributions.

        Returns:
            True if successful.
        """
        try:
            result = subprocess.run(
                [self._executable, "--shutdown"],
                capture_output=True,
                text=True,
                timeout=10,
            )
            return result.returncode == 0
        except Exception:
            return False

    def terminate_distribution(self, distribution: Optional[str] = None) -> bool:
        """
        Terminate a specific WSL distribution.

        Args:
            distribution: Distribution name (defaults to current).

        Returns:
            True if successful.
        """
        distro = distribution or self._distribution or self._detect_default_distribution()
        if not distro:
            return False

        try:
            result = subprocess.run(
                [self._executable, "--terminate", distro],
                capture_output=True,
                text=True,
                timeout=10,
            )
            return result.returncode == 0
        except Exception:
            return False

    def import_distribution(
        self,
        name: str,
        install_path: str,
        root_fs_path: str,
    ) -> bool:
        """
        Import a WSL distribution from a tar file.

        Args:
            name: Name for the new distribution.
            install_path: Directory to store the distribution.
            root_fs_path: Path to the root filesystem tar file.

        Returns:
            True if successful.
        """
        try:
            result = subprocess.run(
                [
                    self._executable,
                    "--import",
                    name,
                    install_path,
                    root_fs_path,
                ],
                capture_output=True,
                text=True,
                timeout=120,
            )
            return result.returncode == 0
        except Exception:
            return False

    def export_distribution(
        self,
        distribution: str,
        file_path: str,
    ) -> bool:
        """
        Export a WSL distribution to a tar file.

        Args:
            distribution: Distribution name to export.
            file_path: Path for the output tar file.

        Returns:
            True if successful.
        """
        try:
            result = subprocess.run(
                [self._executable, "--export", distribution, file_path],
                capture_output=True,
                text=True,
                timeout=300,
            )
            return result.returncode == 0
        except Exception:
            return False


# Register the adapter
BaseAdapter.register(ShellType.WSL)(WSLAdapter)
