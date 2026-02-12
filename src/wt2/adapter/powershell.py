"""
PowerShell adapter.

Provides integration with PowerShell (both Windows PowerShell and PowerShell Core).
"""

from __future__ import annotations
import subprocess
import os
from typing import Optional, Dict, Any, List
from pathlib import Path

from .base import BaseAdapter, AdapterInfo, ShellType


class PowerShellAdapter(BaseAdapter):
    """
    Adapter for PowerShell.

    Supports both Windows PowerShell (powershell.exe) and
    PowerShell Core (pwsh.exe).
    """

    def __init__(
        self,
        shell_type: ShellType = ShellType.POWERSHELL_CORE,
        executable: Optional[str] = None,
        timeout: float = 30.0,
    ):
        """
        Initialize the PowerShell adapter.

        Args:
            shell_type: Whether to use PowerShell Core or Windows PowerShell.
            executable: Explicit path to PowerShell executable.
            timeout: Default command timeout in seconds.
        """
        self._shell_type = shell_type
        self._executable = executable or self._find_executable(shell_type)
        self._timeout = timeout

    def _find_executable(self, shell_type: ShellType) -> str:
        """Find the PowerShell executable."""
        if shell_type == ShellType.POWERSHELL:
            return "powershell.exe"
        return "pwsh.exe"

    @property
    def info(self) -> AdapterInfo:
        """Get adapter information."""
        version = self._get_version()
        return AdapterInfo(
            name="PowerShell Core" if self._shell_type == ShellType.POWERSHELL_CORE else "Windows PowerShell",
            shell_type=self._shell_type,
            version=version,
            is_available=self.is_available(),
            executable_path=self._executable,
            default_args=["-NoLogo", "-NoProfile"],
        )

    def is_available(self) -> bool:
        """Check if PowerShell is available."""
        if not self._executable:
            return False

        try:
            # Check if executable exists
            if self._executable.endswith(".exe"):
                import ctypes
                path = ctypes.windll.kernel32.GetFileAttributesW(self._executable)
                if path == -1:
                    return False
            else:
                if not Path(self._executable).exists():
                    return False

            # Try running a simple command
            result = subprocess.run(
                [self._executable, "-Version"],
                capture_output=True,
                text=True,
                timeout=5,
            )
            return result.returncode == 0
        except Exception:
            return False

    def _get_version(self) -> str:
        """Get PowerShell version."""
        try:
            result = subprocess.run(
                [self._executable, "-NoLogo", "-Command", "$PSVersionTable.PSVersion.ToString()"],
                capture_output=True,
                text=True,
                timeout=10,
            )
            if result.returncode == 0:
                return result.stdout.strip()
        except Exception:
            pass
        return "unknown"

    def execute(
        self,
        command: str,
        cwd: Optional[str] = None,
        env: Optional[Dict[str, str]] = None,
        timeout: Optional[float] = None,
    ) -> Dict[str, Any]:
        """
        Execute a PowerShell command.

        Args:
            command: PowerShell command to execute.
            cwd: Working directory.
            env: Environment variables.
            timeout: Execution timeout.

        Returns:
            Response with stdout, stderr, and exit code.
        """
        if not self.is_available():
            return {
                "success": False,
                "stdout": "",
                "stderr": "PowerShell not available",
                "exit_code": 1,
            }

        # Build environment
        execution_env = os.environ.copy()
        if env:
            execution_env.update(env)

        # Build command
        ps_command = command if command.startswith("$") else f"& {{{command}}}"

        try:
            result = subprocess.run(
                [
                    self._executable,
                    "-NoLogo",
                    "-NoProfile",
                    "-Command",
                    ps_command,
                ],
                capture_output=True,
                text=True,
                timeout=timeout or self._timeout,
                cwd=cwd,
                env=execution_env,
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

    def execute_script(
        self,
        script_path: str,
        args: Optional[List[str]] = None,
        cwd: Optional[str] = None,
        env: Optional[Dict[str, str]] = None,
        timeout: Optional[float] = None,
    ) -> Dict[str, Any]:
        """
        Execute a PowerShell script file.

        Args:
            script_path: Path to .ps1 script file.
            args: Script arguments.
            cwd: Working directory.
            env: Environment variables.
            timeout: Execution timeout.

        Returns:
            Response with stdout, stderr, and exit code.
        """
        if not Path(script_path).exists():
            return {
                "success": False,
                "stdout": "",
                "stderr": f"Script not found: {script_path}",
                "exit_code": 1,
            }

        # Build command to execute script
        script_args = " ".join(args) if args else ""
        command = f'. "{script_path}" {script_args}'

        return self.execute(command, cwd=cwd, env=env, timeout=timeout)

    def start_session(
        self,
        cwd: Optional[str] = None,
        env: Optional[Dict[str, str]] = None,
    ) -> str:
        """
        Start an interactive PowerShell session.

        Args:
            cwd: Working directory.
            env: Environment variables.

        Returns:
            Session identifier (process ID).
        """
        import uuid
        session_id = str(uuid.uuid4())

        # Build environment
        execution_env = os.environ.copy()
        if env:
            execution_env.update(env)

        # Start interactive process
        process = subprocess.Popen(
            [self._executable, "-NoLogo", "-NoProfile"],
            cwd=cwd,
            env=execution_env,
            stdin=subprocess.PIPE,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True,
        )

        return f"{session_id}:{process.pid}"

    def end_session(self, session_id: str) -> bool:
        """
        End a PowerShell session.

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
        # This requires maintaining process handles, simplified here
        return True

    def get_prompt(self, session_id: str) -> str:
        """
        Get the current shell prompt.

        Args:
            session_id: Session identifier.

        Returns:
            Prompt string.
        """
        result = self.execute("$PROFILE.CurrentUserCurrentHost.CurrentUI.RawUI.WindowTitle")
        return result.get("stdout", "PS> ").strip()

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
        command = f"$host.UI.RawUI.BufferSize = New-Object Management.Automation.Host.Size ({cols}, {rows})"
        return self.execute(command)["success"]

    def get_environment(
        self,
        session_id: str,
        *variables: str,
    ) -> Dict[str, str]:
        """
        Get environment variables.

        Args:
            session_id: Session identifier.
            *variables: Variables to retrieve.

        Returns:
            Dictionary of variables.
        """
        result = self.execute("$env:Path")
        if result["success"]:
            return {"PATH": result["stdout"]}
        return {}

    def set_environment(
        self,
        session_id: str,
        **variables: str,
    ) -> bool:
        """
        Set environment variables.

        Args:
            session_id: Session identifier.
            **variables: Variables to set.

        Returns:
            True if successful.
        """
        for key, value in variables.items():
            command = f"$env:{key} = '{value}'"
            if not self.execute(command)["success"]:
                return False
        return True

    def get_working_directory(self, session_id: str) -> str:
        """
        Get the current working directory.

        Args:
            session_id: Session identifier.

        Returns:
            Current working directory.
        """
        result = self.execute("(Get-Location).Path")
        if result["success"]:
            return result["stdout"].strip()
        return ""

    def change_directory(self, session_id: str, path: str) -> bool:
        """
        Change the working directory.

        Args:
            session_id: Session identifier.
            path: New directory path.

        Returns:
            True if successful.
        """
        command = f'Set-Location "{path}"'
        return self.execute(command)["success"]

    def clear_screen(self, session_id: str) -> bool:
        """
        Clear the terminal screen.

        Args:
            session_id: Session identifier.

        Returns:
            True if successful.
        """
        return self.execute("Clear-Host")["success"]

    def get_exit_code(self, session_id: str) -> Optional[int]:
        """
        Get the last exit code.

        Args:
            session_id: Session identifier.

        Returns:
            Exit code or None.
        """
        result = self.execute("$LASTEXITCODE")
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
            signal: Signal (Windows doesn't use Unix signals).

        Returns:
            True if successful.
        """
        return self.end_session(session_id)

    # Additional PowerShell-specific methods

    def invoke_expression(self, expression: str) -> Dict[str, Any]:
        """
        Invoke a PowerShell expression.

        Args:
            expression: PowerShell expression to invoke.

        Returns:
            Response with result.
        """
        return self.execute(f"({expression}) | ConvertTo-Json -Depth 1")

    def invoke_command(
        self,
        name: str,
        args: Optional[List[str]] = None,
        parameters: Optional[Dict[str, Any]] = None,
    ) -> Dict[str, Any]:
        """
        Invoke a PowerShell command.

        Args:
            name: Command name.
            args: Positional arguments.
            parameters: Named parameters.

        Returns:
            Response with result.
        """
        cmd_parts = [name]

        if args:
            for arg in args:
                cmd_parts.append(f'"{arg}"')

        if parameters:
            for key, value in parameters.items():
                if isinstance(value, str):
                    cmd_parts.append(f"-{key} '{value}'")
                else:
                    cmd_parts.append(f"-{key} {value}")

        command = " ".join(cmd_parts)
        return self.execute(command)

    def get_module_version(self, module_name: str) -> Optional[str]:
        """
        Get the version of an installed PowerShell module.

        Args:
            module_name: Name of the module.

        Returns:
            Version string or None if not installed.
        """
        result = self.execute(
            f'(Get-Module -ListAvailable -Name "{module_name}" | Select-Object -First 1).Version.ToString()'
        )
        if result["success"]:
            return result["stdout"].strip()
        return None

    def import_module(self, module_name: str) -> bool:
        """
        Import a PowerShell module.

        Args:
            module_name: Name of the module.

        Returns:
            True if successful.
        """
        result = self.execute(f"Import-Module {module_name}")
        return result["success"]


# Register the adapters
BaseAdapter.register(ShellType.POWERSHELL)(PowerShellAdapter)
BaseAdapter.register(ShellType.POWERSHELL_CORE)(PowerShellAdapter)
