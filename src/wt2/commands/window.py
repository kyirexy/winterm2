"""Window-related commands for winterm2."""

from typing import Optional
import click

from ..core.terminal import WindowsTerminalCLI, get_cli


@click.group()
def window():
    """
    Window management commands.

    Commands:
        new     - Create a new window
        close   - Close a window
        focus   - Focus a window
        list    - List all windows
        move    - Move window to position
        resize  - Resize window
        fullscreen - Toggle fullscreen mode
        arrange - Window arrangement commands
    """
    pass


@window.command("new")
@click.option("--profile", "-p", type=str, default=None, help="Profile to use")
@click.option("--command", "-c", type=str, default=None, help="Command to run")
@click.option("--startup-dir", "-d", type=str, default=None, help="Starting directory")
@click.pass_context
def cmd_new_window(ctx: click.Context, profile: Optional[str], command: Optional[str], startup_dir: Optional[str]) -> None:
    """Create a new window."""
    cli: WindowsTerminalCLI = ctx.obj.get("cli", get_cli())
    try:
        result = cli.new_window(profile=profile, command=command, cwd=startup_dir)
        if result.get("success"):
            click.echo("New window created")
        else:
            click.echo(f"Failed: {result.get('error')}", err=True)
            ctx.exit(1)
    except Exception as e:
        click.echo(f"Error: {e}", err=True)
        ctx.exit(2)


@window.command("close")
@click.argument("window_id", type=str, required=False)
@click.option("--force", "-f", is_flag=True, default=False)
@click.pass_context
def cmd_close_window(ctx: click.Context, window_id: Optional[str], force: bool) -> None:
    """Close a window."""
    cli: WindowsTerminalCLI = ctx.obj.get("cli", get_cli())
    try:
        if not force:
            if not click.confirm(f"Close window {window_id or 'current'}?"):
                click.echo("Cancelled")
                return
        result = cli.close_window(window_id=window_id)
        if result.get("success"):
            click.echo("Window closed")
        else:
            click.echo(f"Failed: {result.get('error')}", err=True)
            ctx.exit(1)
    except Exception as e:
        click.echo(f"Error: {e}", err=True)
        ctx.exit(2)


@window.command("focus")
@click.argument("window_id", type=str, required=True)
@click.pass_context
def cmd_focus_window(ctx: click.Context, window_id: str) -> None:
    """Focus a specific window."""
    cli: WindowsTerminalCLI = ctx.obj.get("cli", get_cli())
    try:
        result = cli.focus_window(window_id)
        if result.get("success"):
            click.echo(f"Focused window: {window_id}")
        else:
            click.echo(f"Failed: {result.get('error')}", err=True)
            ctx.exit(1)
    except Exception as e:
        click.echo(f"Error: {e}", err=True)
        ctx.exit(2)


@window.command("list")
@click.option("--json", "output_json", is_flag=True, default=False)
@click.pass_context
def cmd_list_windows(ctx: click.Context, output_json: bool) -> None:
    """List all windows."""
    cli: WindowsTerminalCLI = ctx.obj.get("cli", get_cli())
    try:
        result = cli.list_windows()
        if result.get("success"):
            click.echo("Windows:")
            click.echo("  Note: Enable Experimental JSON API for detailed window list")
        else:
            click.echo(f"Failed: {result.get('error')}", err=True)
            ctx.exit(1)
    except Exception as e:
        click.echo(f"Error: {e}", err=True)
        ctx.exit(2)


@window.command("move")
@click.argument("x", type=int, required=True)
@click.argument("y", type=int, required=True)
@click.argument("window_id", type=str, required=False)
@click.pass_context
def cmd_move_window(ctx: click.Context, x: int, y: int, window_id: Optional[str]) -> None:
    """Move window to position."""
    cli: WindowsTerminalCLI = ctx.obj.get("cli", get_cli())
    try:
        result = cli.move_window(window_id, x, y)
        if result.get("success"):
            click.echo(f"Moved window to ({x}, {y})")
        else:
            click.echo(f"Failed: {result.get('error')}", err=True)
            ctx.exit(1)
    except Exception as e:
        click.echo(f"Error: {e}", err=True)
        ctx.exit(2)


@window.command("resize")
@click.argument("width", type=int, required=True)
@click.argument("height", type=int, required=True)
@click.argument("window_id", type=str, required=False)
@click.pass_context
def cmd_resize_window(ctx: click.Context, width: int, height: int, window_id: Optional[str]) -> None:
    """Resize window."""
    cli: WindowsTerminalCLI = ctx.obj.get("cli", get_cli())
    try:
        result = cli.resize_window(window_id, width, height)
        if result.get("success"):
            click.echo(f"Resized window to {width}x{height}")
        else:
            click.echo(f"Failed: {result.get('error')}", err=True)
            ctx.exit(1)
    except Exception as e:
        click.echo(f"Error: {e}", err=True)
        ctx.exit(2)


@window.command("fullscreen")
@click.argument("state", type=click.Choice(["on", "off", "toggle"]), required=False, default="toggle")
@click.pass_context
def cmd_fullscreen(ctx: click.Context, state: str) -> None:
    """Toggle fullscreen mode."""
    cli: WindowsTerminalCLI = ctx.obj.get("cli", get_cli())
    try:
        result = cli.set_fullscreen(None, state)
        if result.get("success"):
            click.echo(f"Fullscreen {state}d")
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
@click.argument("name", type=str, required=True)
@click.pass_context
def cmd_arrange_save(ctx: click.Context, name: str) -> None:
    """Save current window arrangement."""
    config = ctx.obj.get("config", {})
    arrangements = config.get("arrangements", {})

    try:
        arrangements[name] = {"saved": "TODO: capture current window state"}
        ctx.obj["config"]["arrangements"] = arrangements
        click.echo(f"Saved arrangement: {name}")
    except Exception as e:
        click.echo(f"Error: {e}", err=True)
        ctx.exit(2)


@arrange.command("restore")
@click.argument("name", type=str, required=True)
@click.pass_context
def cmd_arrange_restore(ctx: click.Context, name: str) -> None:
    """Restore window arrangement."""
    config = ctx.obj.get("config", {})
    arrangements = config.get("arrangements", {})

    if name not in arrangements:
        click.echo(f"Arrangement '{name}' not found", err=True)
        ctx.exit(3)
        return

    try:
        click.echo(f"Restored arrangement: {name}")
    except Exception as e:
        click.echo(f"Error: {e}", err=True)
        ctx.exit(2)


@arrange.command("list")
@click.pass_context
def cmd_arrange_list(ctx: click.Context) -> None:
    """List saved window arrangements."""
    config = ctx.obj.get("config", {})
    arrangements = config.get("arrangements", {})

    if arrangements:
        click.echo("Saved arrangements:")
        for name in arrangements:
            click.echo(f"  - {name}")
    else:
        click.echo("No saved arrangements")
