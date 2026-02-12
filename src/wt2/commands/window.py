"""Window-related commands."""

from typing import Optional, List
import click
import os

from ..core.terminal import WindowsTerminalAPI, get_api
from ..utils.config import WT2Config, ConfigLoader


@click.group()
def window():
    """
    Window management commands.

    Commands:
        new         - Create a new window
        close       - Close a window
        focus       - Focus a window
        list        - List all windows
        move        - Move window to position
        resize      - Resize window
        fullscreen  - Toggle fullscreen mode
        arrange     - Save/restore window arrangements
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
@click.option(
    "--force",
    "-f",
    is_flag=True,
    default=False,
    help="Force close without confirmation",
)
@click.pass_context
def cmd_close_window(ctx: click.Context, window_id: Optional[str], force: bool) -> None:
    """Close a window."""
    api: WindowsTerminalAPI = ctx.obj.get("api", get_api())
    try:
        if not force:
            if not click.confirm(f"Close window {window_id}?"):
                click.echo("Cancelled")
                return
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
@click.option(
    "--json",
    "output_json",
    is_flag=True,
    default=False,
    help="Output as JSON",
)
@click.pass_context
def cmd_list_windows(ctx: click.Context, output_json: bool) -> None:
    """List all windows."""
    api: WindowsTerminalAPI = ctx.obj.get("api", get_api())
    try:
        state = api.get_state()
        windows = state.get("windows", [])
        if not windows:
            click.echo("No windows open")
            return

        if output_json:
            import json
            click.echo(json.dumps({"windows": windows}, indent=2))
        else:
            click.echo("Windows:")
            click.echo("-" * 60)
            for win in windows:
                win_id = win.get("id", "unknown")
                title = win.get("title", "Untitled")
                is_focused = win.get("isFocused", False)
                is_fullscreen = win.get("isFullscreen", False)
                marker = " *" if is_focused else ""
                fullscreen_marker = " [F]" if is_fullscreen else ""
                click.echo(f"[{win_id}] {title}{marker}{fullscreen_marker}")
    except Exception as e:
        click.echo(f"Error: {e}", err=True)
        ctx.exit(2)


@window.command("move")
@click.argument("x", type=int)
@click.argument("y", type=int)
@click.argument("window_id", type=str, required=False)
@click.pass_context
def cmd_move_window(ctx: click.Context, x: int, y: int, window_id: Optional[str]) -> None:
    """Move window to position (pixels)."""
    api: WindowsTerminalAPI = ctx.obj.get("api", get_api())
    try:
        result = api.send_command("moveWindow", windowId=window_id, x=x, y=y)
        if result.get("success"):
            click.echo(f"Moved window to ({x}, {y})")
        else:
            click.echo(f"Failed: {result.get('error')}", err=True)
            ctx.exit(1)
    except Exception as e:
        click.echo(f"Error: {e}", err=True)
        ctx.exit(2)


@window.command("resize")
@click.argument("width", type=int)
@click.argument("height", type=int)
@click.argument("window_id", type=str, required=False)
@click.pass_context
def cmd_resize_window(ctx: click.Context, width: int, height: int, window_id: Optional[str]) -> None:
    """Resize window (pixels)."""
    api: WindowsTerminalAPI = ctx.obj.get("api", get_api())
    try:
        result = api.send_command("resizeWindow", windowId=window_id, width=width, height=height)
        if result.get("success"):
            click.echo(f"Resized window to {width}x{height}")
        else:
            click.echo(f"Failed: {result.get('error')}", err=True)
            ctx.exit(1)
    except Exception as e:
        click.echo(f"Error: {e}", err=True)
        ctx.exit(2)


@window.command("fullscreen")
@click.argument("window_id", type=str, required=False)
@click.option(
    "--state",
    "-s",
    type=click.Choice(["on", "off", "toggle"]),
    default="toggle",
    help="Fullscreen state",
)
@click.pass_context
def cmd_fullscreen(ctx: click.Context, window_id: Optional[str], state: str) -> None:
    """Toggle fullscreen mode."""
    api: WindowsTerminalAPI = ctx.obj.get("api", get_api())
    try:
        is_fullscreen = state == "on" or (state == "toggle" and not api.get_state().get("isFullscreen", False))
        result = api.send_command("setFullscreen", windowId=window_id, fullscreen=is_fullscreen)
        if result.get("success"):
            status = "enabled" if is_fullscreen else "disabled"
            click.echo(f"Fullscreen {status}")
        else:
            click.echo(f"Failed: {result.get('error')}", err=True)
            ctx.exit(1)
    except Exception as e:
        click.echo(f"Error: {e}", err=True)
        ctx.exit(2)


@window.group()
def arrange():
    """Window arrangement commands."""
    pass


@arrange.command("save")
@click.argument("name", type=str)
@click.pass_context
def cmd_arrange_save(ctx: click.Context, name: str) -> None:
    """Save current window arrangement."""
    api: WindowsTerminalAPI = ctx.obj.get("api", get_api())
    try:
        state = api.get_state()
        arrangement = {
            "name": name,
            "windows": state.get("windows", []),
        }
        # Save to config
        loader = ConfigLoader()
        config = loader.load()
        if not hasattr(config, 'arrangements'):
            config.arrangements = {}
        config.arrangements[name] = arrangement
        loader.save(config)
        click.echo(f"Saved arrangement: {name}")
    except Exception as e:
        click.echo(f"Error: {e}", err=True)
        ctx.exit(2)


@arrange.command("restore")
@click.argument("name", type=str)
@click.pass_context
def cmd_arrange_restore(ctx: click.Context, name: str) -> None:
    """Restore window arrangement."""
    api: WindowsTerminalAPI = ctx.obj.get("api", get_api())
    try:
        loader = ConfigLoader()
        config = loader.load()
        arrangements = getattr(config, 'arrangements', {})
        if name not in arrangements:
            click.echo(f"Arrangement '{name}' not found", err=True)
            ctx.exit(3)
        arrangement = arrangements[name]
        # Restore windows
        for win in arrangement.get("windows", []):
            profile = win.get("profile")
            api.send_command("newWindow", profile=profile)
        click.echo(f"Restored arrangement: {name}")
    except Exception as e:
        click.echo(f"Error: {e}", err=True)
        ctx.exit(2)


@arrange.command("list")
@click.pass_context
def cmd_arrange_list(ctx: click.Context) -> None:
    """List saved window arrangements."""
    try:
        loader = ConfigLoader()
        config = loader.load()
        arrangements = getattr(config, 'arrangements', {})
        if not arrangements:
            click.echo("No saved arrangements")
            return
        click.echo("Saved arrangements:")
        for name in arrangements:
            click.echo(f"  - {name}")
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
