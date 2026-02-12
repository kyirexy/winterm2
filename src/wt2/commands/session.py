"""Session-related commands."""

from typing import Optional, List, Dict, Any
from pathlib import Path
import click

from ..core.terminal import WindowsTerminalAPI, get_api


@click.group()
def session():
    """
    Session control commands.

    Commands:
        send    - Send a command
        run     - Run a command
        clear   - Clear the pane
        list    - List sessions
    """
    pass


@session.command("send")
@click.argument("command", type=str, required=True, nargs=-1)
@click.option("--pane-id", type=str, default=None)
@click.pass_context
def cmd_send(ctx: click.Context, command: tuple, pane_id: Optional[str]) -> None:
    """Send a command to the pane."""
    api: WindowsTerminalAPI = ctx.obj.get("api", get_api())
    try:
        cmd_str = " ".join(command)
        result = api.send_text(cmd_str, pane_id=pane_id)
        if result.get("success"):
            click.echo("Command sent")
        else:
            click.echo("Failed", err=True)
            ctx.exit(1)
    except Exception as e:
        click.echo(f"Error: {e}", err=True)
        ctx.exit(2)


@session.command("run")
@click.argument("command", type=str, required=True)
@click.pass_context
def cmd_run(ctx: click.Context, command: str) -> None:
    """Run a command in a new pane."""
    api: WindowsTerminalAPI = ctx.obj.get("api", get_api())
    try:
        result = api.new_pane(command=command)
        if result.get("success"):
            click.echo("Command running")
        else:
            click.echo("Failed", err=True)
            ctx.exit(1)
    except Exception as e:
        click.echo(f"Error: {e}", err=True)
        ctx.exit(2)


@session.command("clear")
@click.pass_context
def cmd_clear(ctx: click.Context) -> None:
    """Clear the pane."""
    api: WindowsTerminalAPI = ctx.obj.get("api", get_api())
    try:
        api.send_text("\x1b[2J\x1b[3J\x1b[H")  # ANSI clear sequence
        click.echo("Cleared")
    except Exception as e:
        click.echo(f"Error: {e}", err=True)
        ctx.exit(2)


@session.command("list")
@click.pass_context
def cmd_list(ctx: click.Context) -> None:
    """List sessions."""
    api: WindowsTerminalAPI = ctx.obj.get("api", get_api())
    try:
        state = api.get_state()
        panes = state.get("panes", [])
        for p in panes:
            p_id = p.get("id", "unknown")
            shell = p.get("shellType", "unknown")
            marker = " *" if p.get("isFocused", False) else ""
            click.echo(f"[{p_id}] {shell}{marker}")
    except Exception as e:
        click.echo(f"Error: {e}", err=True)
        ctx.exit(2)


def start_session(
    profile: Optional[str] = None,
    window_size: Optional[List[int]] = None,
    title: Optional[str] = None,
) -> dict:
    """Start a new session.

    Args:
        profile: The profile to use.
        window_size: The window size as [width, height].
        title: The window title.

    Returns:
        dict: Result of the operation.
    """
    from wt2.commands.window import new_window
    from wt2.commands.tab import new_tab

    try:
        window_result = new_window(profile=profile, size=window_size)
        if not window_result.get("success"):
            return window_result

        tab_result = new_tab(title=title)
        return {
            "success": True,
            "window_id": window_result.get("window_id"),
            "tab_id": tab_result.get("tab_id"),
        }
    except Exception as e:
        return {"success": False, "error": str(e)}


def load_session(config_path: str, profile: str) -> dict:
    """Load a session from a configuration file.

    Args:
        config_path: Path to the configuration file.
        profile: The profile to load.

    Returns:
        dict: Result of the operation.
    """
    from wt2.utils.config import ConfigLoader

    path = Path(config_path)
    if not path.exists():
        return {"success": False, "error": f"Config file not found: {config_path}"}

    loader = ConfigLoader()
    config = loader.load(str(path))
    if config is None:
        return {"success": False, "error": loader.error}

    profile_config = loader.get_profile(profile)
    if profile_config is None:
        return {"success": False, "error": f"Profile not found: {profile}"}

    return start_session(profile=profile_config.get("default_shell"))


def save_session(config_path: str) -> dict:
    """Save the current session state to a file.

    Args:
        config_path: Path to save the configuration.

    Returns:
        dict: Result of the operation.
    """
    from wt2.core.connection import TerminalConnection

    try:
        conn = TerminalConnection()
        conn.connect()

        result = conn.send_message({"action": "getSession"})
        if result.get("success"):
            import yaml
            path = Path(config_path)
            with open(path, "w") as f:
                yaml.dump(result.get("session"), f)
            return {"success": True, "file": str(path)}

        return result
    except Exception as e:
        return {"success": False, "error": str(e)}


def export_session(config_path: str, format: str = "yaml") -> dict:
    """Export the current session to a file.

    Args:
        config_path: Path to save the export.
        format: Export format (yaml or json).

    Returns:
        dict: Result of the operation.
    """
    from wt2.core.connection import TerminalConnection
    from wt2.utils.config import ConfigExporter

    try:
        conn = TerminalConnection()
        conn.connect()

        result = conn.send_message({"action": "getSession"})
        if result.get("success"):
            exporter = ConfigExporter()
            content = exporter.export(result.get("session"), format=format)
            path = Path(config_path)
            with open(path, "w") as f:
                f.write(content)
            return {"success": True, "file": str(path)}

        return result
    except Exception as e:
        return {"success": False, "error": str(e)}


def run_workflow(workflow: Dict[str, Any]) -> dict:
    """Run a workflow.

    Args:
        workflow: The workflow definition.

    Returns:
        dict: Result of the operation.
    """
    steps_completed = 0

    try:
        for step in workflow.get("steps", []):
            if "run_command" in step:
                from wt2.core.connection import TerminalConnection

                conn = TerminalConnection()
                conn.connect()
                conn.send_message({"action": "sendInput", "input": step["run_command"]})
                steps_completed += 1
            elif "load_profile" in step:
                load_session(step["load_profile"], step.get("profile", "default"))
                steps_completed += 1
            elif "focus_tab" in step:
                from wt2.commands.tab import focus_tab

                focus_tab(step["focus_tab"])
                steps_completed += 1

        return {"success": True, "steps_completed": steps_completed}
    except Exception as e:
        return {"success": False, "error": str(e), "steps_completed": steps_completed}
