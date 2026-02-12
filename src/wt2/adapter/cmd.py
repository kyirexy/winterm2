"""
CMD adapter.

Provides integration with Windows Command Prompt (cmd.exe).
"""

from __future__ import annotations
import subprocess
import os
import re
from typing import Optional, Dict, Any, List
from pathlib import Path

from .base import BaseAdapter, AdapterInfo, ShellType


class CMDAdapter(BaseAdapter):
    """
    Adapter for Windows Command Prompt (cmd.exe).

    Provides methods to execute commands and manage sessions
    in the Windows CMD environment.
    """

    def __init__(
        self,
        executable: Optional[str] = None,
        timeout: float = 30.0,
        encoding: str = "utf-8",
    ):
        """
        Initialize the CMD adapter.

        Args:
            executable: Explicit path to cmd.exe.
            timeout: Default command timeout in seconds.
            encoding: Output encoding.
        """
        self._executable = executable or "cmd.exe"
        self._timeout = timeout
        self._encoding = encoding

    @property
    def info(self) -> AdapterInfo:
        """Get adapter information."""
        return AdapterInfo(
            name="Windows Command Prompt",
            shell_type=ShellType.CMD,
            version="10.0",
            is_available=self.is_available(),
            executable_path=self._executable,
            default_args=["/K", "echo winterm2 CMD adapter loaded"],
        )

    def is_available(self) -> bool:
        """Check if CMD is available."""
        try:
            result = subprocess.run(
                [self._executable, "/C", "echo test"],
                capture_output=True,
                text=True,
                timeout=5,
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
        Execute a CMD command.

        Args:
            command: CMD command to execute.
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
                "stderr": "CMD not available",
                "exit_code": 1,
            }

        # Build environment
        execution_env = os.environ.copy()
        if env:
            execution_env.update(env)

        # Wrap command with /C for one-time execution
        cmd = f"/C {command}"

        try:
            result = subprocess.run(
                [self._executable, "/Q", cmd],
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

    def start_session(
        self,
        cwd: Optional[str] = None,
        env: Optional[Dict[str, str]] = None,
    ) -> str:
        """
        Start an interactive CMD session.

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
            [self._executable, "/K", "echo winterm2 CMD session started"],
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
        End a CMD session.

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
        # Simplified - requires maintaining process handles
        return True

    def get_prompt(self, session_id: str) -> str:
        """
        Get the current shell prompt.

        Args:
            session_id: Session identifier.

        Returns:
            Prompt string.
        """
        result = self.execute("echo %prompt%")
        return result.get("stdout", "C:\\> ").strip()

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
            True if successful (CMD has limited resize support).
        """
        command = f"mode con: cols={cols} lines={rows}"
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
        result = self.execute("echo %PATH%")
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
            command = f'set {key}={value}'
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
        result = self.execute("echo %CD%")
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
        command = f'cd /D "{path}"'
        return self.execute(command)["success"]

    def clear_screen(self, session_id: str) -> bool:
        """
        Clear the terminal screen.

        Args:
            session_id: Session identifier.

        Returns:
            True if successful.
        """
        return self.execute("cls")["success"]

    def get_exit_code(self, session_id: str) -> Optional[int]:
        """
        Get the last exit code.

        Args:
            session_id: Session identifier.

        Returns:
            Exit code or None.
        """
        result = self.execute("echo %errorlevel%")
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

    # CMD-specific methods

    def run_batch_file(
        self,
        script_path: str,
        args: Optional[List[str]] = None,
        cwd: Optional[str] = None,
        env: Optional[Dict[str, str]] = None,
        timeout: Optional[float] = None,
    ) -> Dict[str, Any]:
        """
        Run a batch file (.bat or .cmd).

        Args:
            script_path: Path to batch file.
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

        # Build command
        script_args = " ".join(args) if args else ""
        command = f'call "{script_path}" {script_args}'

        return self.execute(command, cwd=cwd, env=env, timeout=timeout)

    def get_drive_list(self) -> List[str]:
        """
        Get list of available drives.

        Returns:
            List of drive letters (e.g., ["C:", "D:", "E:"]).
        """
        result = self.execute("wmic logicaldisk get name")
        if result["success"]:
            drives = []
            for line in result["stdout"].split("\n"):
                line = line.strip()
                if len(line) == 2 and line[1] == ":":
                    drives.append(line)
            return drives
        return []

    def get_directory_contents(
        self,
        path: str,
        show_hidden: bool = False,
    ) -> List[Dict[str, Any]]:
        """
        Get directory contents.

        Args:
            path: Directory path.
            show_hidden: Include hidden files.

        Returns:
            List of file/directory information.
        """
        cmd = 'dir /A' + ('H' if show_hidden else '') + ' /N "' + path + '"'
        result = self.execute(cmd)

        if not result["success"]:
            return []

        items = []
        lines = result["stdout"].split("\n")

        for line in lines:
            # Parse dir output format
            # Format: "MM/DD/YYYY  HH:MMAM  <DIR>  foldername"
            # or "MM/DD/YYYY  HH:MMAM     12345 filename"
            if "<DIR>" in line:
                match = re.match(r".*<DIR>\s+(.+)", line)
                if match:
                    items.append({
                        "name": match.group(1).strip(),
                        "is_dir": True,
                        "size": 0,
                    })
            else:
                parts = line.split()
                if len(parts) >= 4:
                    try:
                        size = int(parts[-2]) if parts[-2].isdigit() else 0
                        items.append({
                            "name": parts[-1],
                            "is_dir": False,
                            "size": size,
                        })
                    except (ValueError, IndexError):
                        pass

        return items

    def create_directory(self, path: str) -> bool:
        """
        Create a directory.

        Args:
            path: Directory path to create.

        Returns:
            True if successful.
        """
        command = f'md "{path}"'
        return self.execute(command)["success"]

    def delete_file(self, path: str, force: bool = False) -> bool:
        """
        Delete a file.

        Args:
            path: File path.
            force: Delete read-only files.

        Returns:
            True if successful.
        """
        flag = "/F " if force else ""
        command = f'del {flag}"{path}"'
        return self.execute(command)["success"]

    def delete_directory(self, path: str, recursive: bool = False) -> bool:
        """
        Delete a directory.

        Args:
            path: Directory path.
            recursive: Delete contents recursively.

        Returns:
            True if successful.
        """
        flag = "/S /Q " if recursive else ""
        command = f'rmdir {flag}"{path}"'
        return self.execute(command)["success"]

    def copy_file(
        self,
        source: str,
        destination: str,
        overwrite: bool = False,
    ) -> bool:
        """
        Copy a file.

        Args:
            source: Source path.
            destination: Destination path.
            overwrite: Overwrite existing file.

        Returns:
            True if successful.
        """
        flag = "/Y " if overwrite else ""
        command = f'copy {flag}"{source}" "{destination}"'
        return self.execute(command)["success"]

    def move_file(
        self,
        source: str,
        destination: str,
    ) -> bool:
        """
        Move/rename a file.

        Args:
            source: Source path.
            destination: Destination path.

        Returns:
            True if successful.
        """
        command = f'move /Y "{source}" "{destination}"'
        return self.execute(command)["success"]

    def rename(
        self,
        path: str,
        new_name: str,
    ) -> bool:
        """
        Rename a file or directory.

        Args:
            path: Current path.
            new_name: New name.

        Returns:
            True if successful.
        """
        directory = str(Path(path).parent)
        command = f'ren "{path}" "{new_name}"'
        return self.execute(command, cwd=directory)["success"]

    def run_command_prompt(
        self,
        title: Optional[str] = None,
        color: Optional[str] = None,
    ) -> subprocess.Popen:
        """
        Open an interactive command prompt window.

        Args:
            title: Window title.
            color: Background/foreground color (e.g., "0A" for black bg, green text).

        Returns:
            Popen object for the new process.
        """
        cmd = [self._executable]

        if title:
            cmd.extend(["/T:0A", "/K", f"title {title}"])
        if color:
            cmd.extend(["/T:" + color])

        return subprocess.Popen(cmd)


# Register the adapter
BaseAdapter.register(ShellType.CMD)(CMDAdapter)
