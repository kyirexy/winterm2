"""WSL adapter."""

import subprocess
from typing import Dict, Any, List, Optional
from wt2.adapters.terminal_adapter import TerminalAdapter


class WSLAdapter(TerminalAdapter):
    """Adapter for WSL (Windows Subsystem for Linux)."""

    name: str = "wsl"

    def execute_command(self, command: str) -> Dict[str, Any]:
        """Execute a command in WSL.

        Args:
            command: The command to execute.

        Returns:
            dict: Result of the operation.
        """
        from wt2.core.connection import TerminalConnection

        conn = TerminalConnection()
        conn.connect()

        return conn.send_message({
            "action": "sendInput",
            "input": f"wsl {command}",
        })

    def get_prompt(self) -> str:
        """Get the WSL prompt.

        Returns:
            str: The prompt.
        """
        from wt2.core.connection import TerminalConnection

        conn = TerminalConnection()
        conn.connect()

        result = conn.send_message({"action": "getPrompt"})
        return result.get("prompt", "$ ")

    def change_directory(self, path: str) -> Dict[str, Any]:
        """Change the current directory in WSL.

        Args:
            path: The directory path.

        Returns:
            dict: Result of the operation.
        """
        # Convert Windows path to WSL path if needed
        wsl_path = self._convert_windows_path(path)
        return self.execute_command(f"cd '{wsl_path}'")

    def _convert_windows_path(self, path: str) -> str:
        """Convert a Windows path to a WSL path.

        Args:
            path: Windows path.

        Returns:
            str: WSL path.
        """
        if path.startswith("\\\\"):
            # Network path
            return path

        # Convert drive letter
        if len(path) >= 2 and path[1] == ":":
            drive = path[0].lower()
            rest = path[2:].replace("\\", "/")
            return f"/mnt/{drive}/{rest}"

        return path

    def execute_windows_command(self, command: str) -> Dict[str, Any]:
        """Execute a Windows command from WSL.

        Args:
            command: The Windows command.

        Returns:
            dict: Result of the operation.
        """
        return self.execute_command(f"wsl.exe {command}")

    def list_distributions(self) -> Dict[str, Any]:
        """List available WSL distributions.

        Returns:
            dict: List of distributions.
        """
        from wt2.core.connection import TerminalConnection

        conn = TerminalConnection()
        conn.connect()

        return conn.send_message({"action": "listDistros"})

    def set_default_distro(self, distro_name: str) -> Dict[str, Any]:
        """Set the default WSL distribution.

        Args:
            distro_name: The distribution name.

        Returns:
            dict: Result of the operation.
        """
        return self.execute_command(f"wsl.exe --setdefault {distro_name}")

    def run_as_user(self, username: str, command: str) -> Dict[str, Any]:
        """Run a command as a specific user.

        Args:
            username: The username.
            command: The command to run.

        Returns:
            dict: Result of the operation.
        """
        return self.execute_command(f"wsl.exe --user {username} {command}")

    def get_mount_points(self) -> Dict[str, Any]:
        """Get WSL mount points.

        Returns:
            dict: Mount point information.
        """
        result = self.execute_command("mount")
        return {"mounts": result}

    def export_distro(self, distro_name: str, export_path: str) -> Dict[str, Any]:
        """Export a WSL distribution.

        Args:
            distro_name: The distribution name.
            export_path: Path to save the export.

        Returns:
            dict: Result of the operation.
        """
        return self.execute_windows_command(
            f"--export {distro_name} {export_path}"
        )

    def import_distro(
        self, distro_name: str, import_path: str, root_path: str
    ) -> Dict[str, Any]:
        """Import a WSL distribution.

        Args:
            distro_name: The distribution name.
            import_path: Path to the root filesystem tarball.
            root_path: Path for the WSL distribution root.

        Returns:
            dict: Result of the operation.
        """
        return self.execute_windows_command(
            f"--import {distro_name} {root_path} {import_path}"
        )

    def get_wsl_version(self) -> str:
        """Get the WSL version.

        Returns:
            str: WSL version.
        """
        result = self.execute_windows_command("--version")
        return result.get("output", "unknown")

    def shutdown(self) -> Dict[str, Any]:
        """Shutdown WSL.

        Returns:
            dict: Result of the operation.
        """
        return self.execute_windows_command("--shutdown")

    def terminate_distro(self, distro_name: str) -> Dict[str, Any]:
        """Terminate a WSL distribution.

        Args:
            distro_name: The distribution name.

        Returns:
            dict: Result of the operation.
        """
        return self.execute_windows_command(f"--terminate {distro_name}")
