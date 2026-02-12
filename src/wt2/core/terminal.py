"""
Windows Terminal API connection module using wt.exe command-line tool.

Uses subprocess to communicate with Windows Terminal via wt.exe,
which is the recommended way to control Windows Terminal.
"""

from __future__ import annotations
import json
import subprocess
import os
from typing import Optional, Dict, Any, List
from pathlib import Path


class WindowsTerminalCLI:
    """Interface to Windows Terminal via wt.exe CLI."""

    def __init__(self):
        """Initialize the Windows Terminal CLI interface."""
        self._wt_path: Optional[str] = None
        self._find_wt()

    def _find_wt(self) -> Optional[str]:
        """Find wt.exe path."""
        import glob

        # Common locations for wt.exe
        possible_paths = [
            # Windows Terminal Store version (find actual exe in package folder)
            os.path.expandvars(r"%LOCALAPPDATA%\Microsoft\WindowsApps\Microsoft.WindowsTerminal_*\wt.exe"),
            # Windows Terminal (winget/installed version)
            os.path.expandvars(r"%PROGRAMFILES%\WindowsApps\Microsoft.WindowsTerminal_*\wt.exe"),
            os.path.expandvars(r"%PROGRAMFILES%\Windows Terminal\wt.exe"),
        ]

        for pattern in possible_paths:
            expanded = os.path.expandvars(pattern)
            matches = glob.glob(expanded)
            for match in matches:
                if os.path.exists(match):
                    self._wt_path = match
                    return self._wt_path

        # Try using where command
        try:
            result = subprocess.run(
                ["where", "wt.exe"],
                capture_output=True,
                text=True,
                timeout=5,
            )
            if result.returncode == 0:
                # Get the first valid path
                for line in result.stdout.strip().split('\n'):
                    if line.strip() and os.path.exists(line.strip()):
                        self._wt_path = line.strip()
                        return self._wt_path
        except Exception:
            pass

        # Try running wt.exe directly (it might be in PATH via WindowsApps alias)
        try:
            result = subprocess.run(
                ["wt.exe", "--version"],
                capture_output=True,
                text=True,
                timeout=5,
            )
            if result.returncode == 0:
                self._wt_path = "wt.exe"
                return self._wt_path
        except Exception:
            pass

        self._wt_path = "wt.exe"
        return self._wt_path

    @property
    def wt_path(self) -> str:
        """Get wt.exe path."""
        if self._wt_path is None:
            self._find_wt()
        return self._wt_path or "wt.exe"

    def _run_wt(self, args: List[str], timeout: float = 10.0) -> subprocess.CompletedProcess:
        """Run wt.exe with given arguments."""
        cmd = [self.wt_path] + args
        try:
            return subprocess.run(
                cmd,
                capture_output=True,
                text=True,
                timeout=timeout,
            )
        except subprocess.TimeoutExpired:
            return subprocess.CompletedProcess(cmd, returncode=-1, stdout="", stderr="Command timed out")
        except FileNotFoundError:
            return subprocess.CompletedProcess(cmd, returncode=-1, stdout="", stderr="wt.exe not found")

    # =========================================================================
    # Window Commands
    # =========================================================================

    def new_window(
        self,
        profile: Optional[str] = None,
        command: Optional[str] = None,
        cwd: Optional[str] = None,
    ) -> Dict[str, Any]:
        """Create a new window."""
        args = ["new-window"]

        if profile:
            args.extend(["--profile", profile])
        if command:
            args.extend(["--command", command])
        if cwd:
            args.extend(["--startingDirectory", cwd])

        result = self._run_wt(args)

        # wt.exe new-window doesn't return JSON, but succeeds with no output
        if result.returncode == 0:
            return {"success": True, "message": "New window created"}
        else:
            return {"success": False, "error": result.stderr.strip()}

    def close_window(self, window_id: Optional[str] = None) -> Dict[str, Any]:
        """Close a window."""
        args = ["close-window"]
        if window_id:
            args.append(window_id)

        result = self._run_wt(args)
        return {"success": result.returncode == 0, "error": result.stderr.strip() if result.returncode != 0 else None}

    def list_windows(self) -> Dict[str, Any]:
        """List all windows (using Windows Terminal API via wt)."""
        # Note: wt.exe doesn't have a direct list-windows command
        # This is a placeholder that returns info about the command availability
        return {
            "success": True,
            "message": "Window listing via wt.exe",
            "note": "Use Windows Terminal directly or enable Experimental JSON API for full state access"
        }

    def focus_window(self, window_id: str) -> Dict[str, Any]:
        """Focus a window."""
        # wt.exe doesn't have a direct focus command
        return {"success": False, "error": "Not implemented in wt.exe"}

    def move_window(self, window_id: Optional[str], x: int, y: int) -> Dict[str, Any]:
        """Move window to position."""
        return {"success": False, "error": "Not implemented in wt.exe"}

    def resize_window(self, window_id: Optional[str], width: int, height: int) -> Dict[str, Any]:
        """Resize window."""
        return {"success": False, "error": "Not implemented in wt.exe"}

    def set_fullscreen(self, window_id: Optional[str], state: str) -> Dict[str, Any]:
        """Set fullscreen mode."""
        args = ["full-screen"]
        result = self._run_wt(args)
        return {"success": result.returncode == 0, "error": result.stderr.strip() if result.returncode != 0 else None}

    # =========================================================================
    # Tab Commands
    # =========================================================================

    def new_tab(
        self,
        profile: Optional[str] = None,
        command: Optional[str] = None,
        cwd: Optional[str] = None,
        window_id: Optional[str] = None,
        title: Optional[str] = None,
    ) -> Dict[str, Any]:
        """Create a new tab."""
        args = ["new-tab"]

        if profile:
            args.extend(["--profile", profile])
        if command:
            args.extend(["--command", command])
        if cwd:
            args.extend(["--startingDirectory", cwd])
        if title:
            args.extend(["--title", title])
        if window_id:
            args.extend(["--window", window_id])

        result = self._run_wt(args)
        return {"success": result.returncode == 0, "error": result.stderr.strip() if result.returncode != 0 else None}

    def close_tab(self, tab_id: str) -> Dict[str, Any]:
        """Close a tab."""
        args = ["close-tab", "--id", tab_id]
        result = self._run_wt(args)
        return {"success": result.returncode == 0, "error": result.stderr.strip() if result.returncode != 0 else None}

    def focus_tab(self, tab_id: str) -> Dict[str, Any]:
        """Focus a tab."""
        args = ["focus-tab", "--id", tab_id]
        result = self._run_wt(args)
        return {"success": result.returncode == 0, "error": result.stderr.strip() if result.returncode != 0 else None}

    def list_tabs(self) -> Dict[str, Any]:
        """List tabs."""
        return {"success": True, "message": "Use wt.exe list-tabs not available"}

    def rename_tab(self, tab_id: Optional[str], title: str) -> Dict[str, Any]:
        """Rename tab."""
        args = ["rename-tab", title]
        if tab_id:
            args.extend(["--id", tab_id])
        result = self._run_wt(args)
        return {"success": result.returncode == 0, "error": result.stderr.strip() if result.returncode != 0 else None}

    # =========================================================================
    # Pane Commands
    # =========================================================================

    def split_pane(
        self,
        direction: str = "horizontal",
        profile: Optional[str] = None,
        command: Optional[str] = None,
        cwd: Optional[str] = None,
        size: Optional[float] = None,
        pane_id: Optional[str] = None,
    ) -> Dict[str, Any]:
        """Split a pane."""
        args = ["split-pane", "--" + direction]

        if profile:
            args.extend(["--profile", profile])
        if command:
            args.extend(["--command", command])
        if cwd:
            args.extend(["--startingDirectory", cwd])
        if size is not None:
            args.extend(["--size", str(size)])
        if pane_id:
            args.extend(["--id", pane_id])

        result = self._run_wt(args)
        return {"success": result.returncode == 0, "error": result.stderr.strip() if result.returncode != 0 else None}

    def close_pane(self, pane_id: Optional[str] = None) -> Dict[str, Any]:
        """Close a pane."""
        args = ["close-pane"]
        if pane_id:
            args.extend(["--id", pane_id])
        result = self._run_wt(args)
        return {"success": result.returncode == 0, "error": result.stderr.strip() if result.returncode != 0 else None}

    def focus_pane(self, direction: str, pane_id: Optional[str] = None) -> Dict[str, Any]:
        """Focus a pane in given direction."""
        args = ["focus-pane", "--" + direction]
        if pane_id:
            args.extend(["--id", pane_id])
        result = self._run_wt(args)
        return {"success": result.returncode == 0, "error": result.stderr.strip() if result.returncode != 0 else None}

    def resize_pane(self, direction: str, delta: int, pane_id: Optional[str] = None) -> Dict[str, Any]:
        """Resize a pane."""
        args = ["resize-pane", "--" + direction, str(delta)]
        if pane_id:
            args.extend(["--id", pane_id])
        result = self._run_wt(args)
        return {"success": result.returncode == 0, "error": result.stderr.strip() if result.returncode != 0 else None}

    def toggle_pane_zoom(self, pane_id: Optional[str] = None) -> Dict[str, Any]:
        """Toggle pane zoom."""
        args = ["toggle-pane-zoom"]
        if pane_id:
            args.extend(["--id", pane_id])
        result = self._run_wt(args)
        return {"success": result.returncode == 0, "error": result.stderr.strip() if result.returncode != 0 else None}

    # =========================================================================
    # Session Commands
    # =========================================================================

    def send_text(self, text: str, pane_id: Optional[str] = None) -> Dict[str, Any]:
        """Send text to a pane."""
        args = ["send-input"]
        if pane_id:
            args.extend(["--id", pane_id])

        result = self._run_wt(args + [text])
        return {"success": result.returncode == 0, "error": result.stderr.strip() if result.returncode != 0 else None}

    def clear_screen(self, pane_id: Optional[str] = None) -> Dict[str, Any]:
        """Clear screen."""
        # Send ANSI clear sequence
        return self.send_text("\x1b[2J\x1b[3J\x1b[H", pane_id=pane_id)

    def set_pane_title(self, title: str, pane_id: Optional[str] = None) -> Dict[str, Any]:
        """Set pane title."""
        args = ["set-title"]
        if pane_id:
            args.extend(["--id", pane_id])
        args.append(title)

        result = self._run_wt(args)
        return {"success": result.returncode == 0, "error": result.stderr.strip() if result.returncode != 0 else None}

    # =========================================================================
    # Utility Commands
    # =========================================================================

    def get_version(self) -> Dict[str, Any]:
        """Get Windows Terminal version."""
        result = self._run_wt(["--version"])
        if result.returncode == 0:
            return {"success": True, "version": result.stdout.strip()}
        return {"success": False, "error": result.stderr.strip()}

    def list_profiles(self) -> Dict[str, Any]:
        """List available profiles."""
        result = self._run_wt(["list-profiles"])
        if result.returncode == 0:
            return {"success": True, "profiles": result.stdout.strip().split('\n')}
        return {"success": False, "error": result.stderr.strip()}


# Export both names for backwards compatibility
WindowsTerminalAPI = WindowsTerminalCLI

# Singleton instance
_cli_instance: Optional[WindowsTerminalCLI] = None


def get_cli() -> WindowsTerminalCLI:
    """Get or create the singleton CLI instance."""
    global _cli_instance
    if _cli_instance is None:
        _cli_instance = WindowsTerminalCLI()
    return _cli_instance


def get_api() -> WindowsTerminalAPI:
    """Get or create the singleton API instance (alias for get_cli)."""
    return get_cli()
