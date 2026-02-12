"""Window-related commands."""

from typing import Optional, List
import click

from ..core.terminal import WindowsTerminalAPI, get_api


@click.group()
def window():
    """
    Window management commands.

    Commands:
        new     - Create a new window
        close   - Close a window
        focus   - Focus a window
        list    - List all windows
    """
    pass


@window.command("new")
@click.option(
    "--profile",
    "-p",
    type=str,
    default=None,
    help="Terminal profile to use",
)
@click.option(
    "--size",
    "-s",
    type=str,
    default=None,
    help="Window size as 'width,height'",
)
@click.option(
    "--startup-dir",
    "-d",
    type=str,
    default=None,
    help="Starting directory",
)
@click.pass_context
def cmd_new_window(
    ctx: click.Context,
    profile: Optional[str],
    size: Optional[str],
    startup_dir: Optional[str],
) -> None:
    """Create a new window."""
    api: WindowsTerminalAPI = ctx.obj.get("api", get_api())

    try:
        width: Optional[int] = None
        height: Optional[int] = None
        if size:
            parts = size.split(",")
            if len(parts) == 2:
                width, height = int(parts[0]), int(parts[1])

        params = {"profile": profile or ctx.obj.get("profile")}
        if width and height:
            params["size"] = [width, height]
        if startup_dir:
            params["cwd"] = startup_dir

        result = api.send_command("newWindow", **params)
        if result.get("success"):
            click.echo(f"Created new window")
        else:
            click.echo(f"Failed: {result.get('error')}", err=True)
            ctx.exit(1)
    except Exception as e:
        click.echo(f"Error: {e}", err=True)
        ctx.exit(2)


@window.command("close")
@click.argument("window_id", type=str, required=False)
@click.pass_context
def cmd_close_window(ctx: click.Context, window_id: Optional[str]) -> None:
    """Close a window."""
    api: WindowsTerminalAPI = ctx.obj.get("api", get_api())
    try:
        result = api.send_command("closeWindow", windowId=window_id)
        if result.get("success"):
            click.echo(f"Closed window {window_id}")
        else:
            click.echo(f"Failed", err=True)
            ctx.exit(1)
    except Exception as e:
        click.echo(f"Error: {e}", err=True)
        ctx.exit(2)


@window.command("focus")
@click.argument("window_id", type=str, required=True)
@click.pass_context
def cmd_focus_window(ctx: click.Context, window_id: str) -> None:
    """Focus a window."""
    api: WindowsTerminalAPI = ctx.obj.get("api", get_api())
    try:
        result = api.send_command("focusWindow", windowId=window_id)
        if result.get("success"):
            click.echo(f"Focused window {window_id}")
        else:
            click.echo(f"Failed", err=True)
            ctx.exit(1)
    except Exception as e:
        click.echo(f"Error: {e}", err=True)
        ctx.exit(2)


@window.command("list")
@click.pass_context
def cmd_list_windows(ctx: click.Context) -> None:
    """List all windows."""
    api: WindowsTerminalAPI = ctx.obj.get("api", get_api())
    try:
        state = api.get_state()
        windows = state.get("windows", [])
        if not windows:
            click.echo("No windows open")
            return
        for win in windows:
            win_id = win.get("id", "unknown")
            title = win.get("title", "Untitled")
            is_focused = win.get("isFocused", False)
            marker = " *" if is_focused else ""
            click.echo(f"[{win_id}] {title}{marker}")
    except Exception as e:
        click.echo(f"Error: {e}", err=True)
        ctx.exit(2)


def new_window(
    profile: Optional[str] = None,
    size: Optional[List[int]] = None,
    startup_dir: Optional[str] = None,
) -> dict:
    """Create a new Windows Terminal window.

    Args:
        profile: The profile to use for the new window.
        size: The size of the window as [width, height].
        startup_dir: The startup directory for the window.

    Returns:
        dict: Result of the operation.
    """
    from wt2.core.connection import TerminalConnection

    try:
        conn = TerminalConnection()
        conn.connect()

        action = {
            "action": "newWindow",
        }

        if profile:
            action["profile"] = profile
        if size:
            action["size"] = size
        if startup_dir:
            action["startupDir"] = startup_dir

        result = conn.send_message(action)
        return result
    except Exception as e:
        return {"success": False, "error": str(e)}


def close_window(window_id: int) -> dict:
    """Close a Windows Terminal window.

    Args:
        window_id: The ID of the window to close.

    Returns:
        dict: Result of the operation.
    """
    from wt2.core.connection import TerminalConnection

    try:
        conn = TerminalConnection()
        conn.connect()

        result = conn.send_message({
            "action": "closeWindow",
            "windowId": window_id,
        })
        return result
    except Exception as e:
        return {"success": False, "error": str(e)}


def focus_window(window_id: int) -> dict:
    """Focus a Windows Terminal window.

    Args:
        window_id: The ID of the window to focus.

    Returns:
        dict: Result of the operation.
    """
    from wt2.core.connection import TerminalConnection

    try:
        conn = TerminalConnection()
        conn.connect()

        result = conn.send_message({
            "action": "focusWindow",
            "windowId": window_id,
        })
        return result
    except Exception as e:
        return {"success": False, "error": str(e)}
