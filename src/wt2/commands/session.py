"""Session-related commands."""

from typing import Optional, List, Dict, Any
from pathlib import Path
import click
import os

from ..core.terminal import WindowsTerminalAPI, get_api


@click.group()
def session():
    """
    Session control commands.

    Commands:
        send        - Send a command
        run         - Run a command
        clear       - Clear the pane
        list        - List sessions
        restart     - Restart session
        focus       - Focus a session/pane
        read        - Read screen contents
        capture     - Capture screen to file
        set-name    - Set session name
        get-var     - Get session variable
        set-var     - Set session variable
    """
    pass


@session.command("send")
@click.argument("command", type=str, required=True, nargs=-1)
@click.option("--pane-id", type=str, default=None)
@click.pass_context
def cmd_send(ctx: click.Context, command: tuple, pane_id: Optional[str]) -> None:
    """Send a command to the pane (no newline)."""
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
@click.option("--pane-id", type=str, default=None)
@click.pass_context
def cmd_run(ctx: click.Context, command: str, pane_id: Optional[str]) -> None:
    """Run a command in the pane (with newline)."""
    api: WindowsTerminalAPI = ctx.obj.get("api", get_api())
    try:
        result = api.send_text(command + "\r", pane_id=pane_id)
        if result.get("success"):
            click.echo("Command executed")
        else:
            click.echo("Failed", err=True)
            ctx.exit(1)
    except Exception as e:
        click.echo(f"Error: {e}", err=True)
        ctx.exit(2)


@session.command("clear")
@click.option("--pane-id", type=str, default=None)
@click.pass_context
def cmd_clear(ctx: click.Context, pane_id: Optional[str]) -> None:
    """Clear the pane."""
    api: WindowsTerminalAPI = ctx.obj.get("api", get_api())
    try:
        api.send_text("\x1b[2J\x1b[3J\x1b[H", pane_id=pane_id)  # ANSI clear sequence
        click.echo("Cleared")
    except Exception as e:
        click.echo(f"Error: {e}", err=True)
        ctx.exit(2)


@session.command("list")
@click.option("--json", "output_json", is_flag=True, default=False)
@click.pass_context
def cmd_list(ctx: click.Context, output_json: bool) -> None:
    """List all sessions/panes."""
    api: WindowsTerminalAPI = ctx.obj.get("api", get_api())
    try:
        state = api.get_state()
        panes = state.get("panes", [])

        if output_json:
            import json
            click.echo(json.dumps({"sessions": panes}, indent=2))
        else:
            click.echo("Sessions:")
            click.echo("-" * 60)
            for p in panes:
                p_id = p.get("id", "unknown")
                shell = p.get("shellType", "unknown")
                title = p.get("title", "")
                marker = " *" if p.get("isFocused", False) else ""
                click.echo(f"[{p_id}] {shell}{marker} {title}")
    except Exception as e:
        click.echo(f"Error: {e}", err=True)
        ctx.exit(2)


@session.command("restart")
@click.option("--pane-id", type=str, default=None)
@click.pass_context
def cmd_restart(ctx: click.Context, pane_id: Optional[str]) -> None:
    """Restart the session."""
    api: WindowsTerminalAPI = ctx.obj.get("api", get_api())
    try:
        result = api.send_command("restartSession", paneId=pane_id)
        if result.get("success"):
            click.echo("Session restarted")
        else:
            click.echo("Failed", err=True)
            ctx.exit(1)
    except Exception as e:
        click.echo(f"Error: {e}", err=True)
        ctx.exit(2)


@session.command("focus")
@click.argument("pane_id", type=str, required=True)
@click.pass_context
def cmd_focus(ctx: click.Context, pane_id: str) -> None:
    """Focus a specific pane."""
    api: WindowsTerminalAPI = ctx.obj.get("api", get_api())
    try:
        result = api.send_command("focusPane", paneId=pane_id)
        if result.get("success"):
            click.echo(f"Focused pane: {pane_id}")
        else:
            click.echo("Failed", err=True)
            ctx.exit(1)
    except Exception as e:
        click.echo(f"Error: {e}", err=True)
        ctx.exit(2)


@session.command("read")
@click.option("--pane-id", type=str, default=None)
@click.option("--lines", "-n", type=int, default=None, help="Number of lines to read")
@click.pass_context
def cmd_read(ctx: click.Context, pane_id: Optional[str], lines: Optional[int]) -> None:
    """Read screen contents."""
    api: WindowsTerminalAPI = ctx.obj.get("api", get_api())
    try:
        state = api.get_state()
        panes = state.get("panes", [])
        target_pane = pane_id

        if not target_pane:
            for p in panes:
                if p.get("isFocused", False):
                    target_pane = p.get("id")
                    break

        for p in panes:
            if p.get("id") == target_pane:
                contents = p.get("content", "")
                content_lines = contents.split("\n")

                if lines:
                    content_lines = content_lines[-lines:]

                click.echo("\n".join(content_lines))
                break
    except Exception as e:
        click.echo(f"Error: {e}", err=True)
        ctx.exit(2)


@session.command("capture")
@click.option("--pane-id", type=str, default=None)
@click.option("--output", "-o", type=str, required=True, help="Output file path")
@click.option("--history", is_flag=True, default=False, help="Include scrollback history")
@click.pass_context
def cmd_capture(ctx: click.Context, pane_id: Optional[str], output: str, history: bool) -> None:
    """Capture screen to file."""
    api: WindowsTerminalAPI = ctx.obj.get("api", get_api())
    try:
        state = api.get_state()
        panes = state.get("panes", [])
        target_pane = pane_id

        if not target_pane:
            for p in panes:
                if p.get("isFocused", False):
                    target_pane = p.get("id")
                    break

        for p in panes:
            if p.get("id") == target_pane:
                contents = p.get("content", "")

                with open(output, "w", encoding="utf-8") as f:
                    f.write(contents)

                click.echo(f"Screen captured to: {output}")
                break
    except Exception as e:
        click.echo(f"Error: {e}", err=True)
        ctx.exit(2)


@session.command("set-name")
@click.argument("name", type=str, required=True)
@click.option("--pane-id", type=str, default=None)
@click.pass_context
def cmd_set_name(ctx: click.Context, name: str, pane_id: Optional[str]) -> None:
    """Set session name."""
    api: WindowsTerminalAPI = ctx.obj.get("api", get_api())
    try:
        result = api.send_command("setPaneTitle", paneId=pane_id, title=name)
        if result.get("success"):
            click.echo(f"Session name set to: {name}")
        else:
            click.echo("Failed", err=True)
            ctx.exit(1)
    except Exception as e:
        click.echo(f"Error: {e}", err=True)
        ctx.exit(2)


@session.command("get-var")
@click.argument("variable", type=str, required=True)
@click.option("--pane-id", type=str, default=None)
@click.pass_context
def cmd_get_var(ctx: click.Context, variable: str, pane_id: Optional[str]) -> None:
    """Get session variable value."""
    api: WindowsTerminalAPI = ctx.obj.get("api", get_api())
    try:
        state = api.get_state()
        panes = state.get("panes", [])
        target_pane = pane_id

        if not target_pane:
            for p in panes:
                if p.get("isFocused", False):
                    target_pane = p.get("id")
                    break

        for p in panes:
            if p.get("id") == target_pane:
                variables = p.get("variables", {})
                value = variables.get(variable)
                if value is not None:
                    click.echo(value)
                else:
                    click.echo(f"Variable '{variable}' not set")
                break
    except Exception as e:
        click.echo(f"Error: {e}", err=True)
        ctx.exit(2)


@session.command("set-var")
@click.argument("variable", type=str, required=True)
@click.argument("value", type=str, required=True)
@click.option("--pane-id", type=str, default=None)
@click.pass_context
def cmd_set_var(ctx: click.Context, variable: str, value: str, pane_id: Optional[str]) -> None:
    """Set session variable value."""
    api: WindowsTerminalAPI = ctx.obj.get("api", get_api())
    try:
        result = api.send_command("setVariable", paneId=pane_id, variable=variable, value=value)
        if result.get("success"):
            click.echo(f"Set {variable} = {value}")
        else:
            click.echo("Failed", err=True)
            ctx.exit(1)
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
