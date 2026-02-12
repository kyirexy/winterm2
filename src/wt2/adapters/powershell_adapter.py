"""PowerShell adapter."""

import base64
from typing import Dict, Any
from wt2.adapters.terminal_adapter import TerminalAdapter


class PowerShellAdapter(TerminalAdapter):
    """Adapter for PowerShell terminal."""

    name: str = "powershell"

    def execute_command(self, command: str) -> Dict[str, Any]:
        """Execute a command in PowerShell.

        Args:
            command: The command to execute.

        Returns:
            dict: Result of the operation.
        """
        from wt2.core.connection import TerminalConnection

        conn = TerminalConnection()
        conn.connect()

        encoded_command = self._encode_command(command)
        return conn.send_message({
            "action": "sendInput",
            "input": encoded_command,
        })

    def get_prompt(self) -> str:
        """Get the PowerShell prompt.

        Returns:
            str: The prompt.
        """
        from wt2.core.connection import TerminalConnection

        conn = TerminalConnection()
        conn.connect()

        result = conn.send_message({"action": "getPrompt"})
        return result.get("prompt", "PS > ")

    def change_directory(self, path: str) -> Dict[str, Any]:
        """Change the current directory in PowerShell.

        Args:
            path: The directory path.

        Returns:
            dict: Result of the operation.
        """
        return self.execute_command(f"Set-Location -Path '{path}'")

    def _encode_command(self, command: str) -> str:
        """Encode a command for PowerShell execution.

        Args:
            command: The command to encode.

        Returns:
            str: Encoded command.
        """
        encoded = base64.b64encode(command.encode("utf-16-le")).decode("ascii")
        return f"powershell -EncodedCommand {encoded}"

    def get_version(self) -> str:
        """Get PowerShell version.

        Returns:
            str: PowerShell version.
        """
        from wt2.core.connection import TerminalConnection

        conn = TerminalConnection()
        conn.connect()

        result = conn.send_message({"action": "getVersion"})
        return result.get("version", "unknown")

    def load_profile(self, profile_path: str) -> Dict[str, Any]:
        """Load a PowerShell profile.

        Args:
            profile_path: Path to the profile file.

        Returns:
            dict: Result of the operation.
        """
        return self.execute_command(f". '{profile_path}'")

    def import_module(self, module_name: str) -> Dict[str, Any]:
        """Import a PowerShell module.

        Args:
            module_name: The module name.

        Returns:
            dict: Result of the operation.
        """
        return self.execute_command(f"Import-Module {module_name}")

    def get_env(self, var_name: str) -> Dict[str, Any]:
        """Get an environment variable.

        Args:
            var_name: The variable name.

        Returns:
            dict: Result with the value.
        """
        result = self.execute_command(f"$env:{var_name}")
        return {"value": result.get("output", "")}

    def set_env(self, var_name: str, value: str) -> Dict[str, Any]:
        """Set an environment variable.

        Args:
            var_name: The variable name.
            value: The value to set.

        Returns:
            dict: Result of the operation.
        """
        return self.execute_command(f"$env:{var_name} = '{value}'")

    def new_alias(self, alias_name: str, command: str) -> Dict[str, Any]:
        """Create a new alias.

        Args:
            alias_name: The alias name.
            command: The command to alias.

        Returns:
            dict: Result of the operation.
        """
        return self.execute_command(f"Set-Alias -Name {alias_name} -Value '{command}'")

    def execute_multi(self, commands: list) -> Dict[str, Any]:
        """Execute multiple commands.

        Args:
            commands: List of commands.

        Returns:
            dict: Result of the operation.
        """
        full_command = "; ".join(commands)
        return self.execute_command(full_command)
